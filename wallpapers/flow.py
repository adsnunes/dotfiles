#!/usr/bin/env python3
"""Papel de parede: linhas de corrente de um escoamento turbulento atrás de um cilindro (esteira de von Kármán).

Campo de velocidade (unidades de pixel, tela 1366x768, escoamento da esquerda para a direita):
- escoamento potencial em torno do cilindro: u - iv = U (1 - a²/z²)
- esteira: duas fileiras alternadas de vórtices de Lamb-Oseen que crescem e enfraquecem rio abaixo
- turbulência: rotacional de uma soma de modos de Fourier aleatórios, com amplitude que cresce dentro da esteira
As linhas são integradas por RK4 e desenhadas como polilinhas finas num SVG.

uso: python3 flow.py dark|light > out.svg
"""
import math
import sys

import numpy as np

W, H = 1366, 768
MODE = sys.argv[1] if len(sys.argv) > 1 else "dark"
PAL = {
    "dark": dict(bg="#2f3134", ink="#d0d1d2", soft="#8b8e92", faint="#5c5f63"),
    "light": dict(bg="#e8e6e1", ink="#2f3134", soft="#5e6064", faint="#a9aaa8"),
}[MODE]

SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1962
rng = np.random.default_rng(SEED)
U = 1.0
CX, CY, A = 300.0, 420.0, 34.0

# vórtices da esteira: (x, y, circulação, raio do núcleo)
vort = []
spacing, half = 118.0, 30.0
for k in range(12):
    x = CX + 95 + k * spacing + rng.normal(0, 8)
    y = CY + (half if k % 2 else -half) * (1 + 0.06 * k) + rng.normal(0, 5)
    gamma = (1 if k % 2 else -1) * 230.0 * math.exp(-0.06 * k) * rng.uniform(0.85, 1.15)
    rc = 20.0 + 3.2 * k
    vort.append((x, y, gamma, rc))
vort = np.array(vort)

# modos de Fourier para a turbulência
NM = 48
kmag = np.exp(rng.uniform(math.log(0.012), math.log(0.09), NM))
kang = rng.uniform(0, 2 * math.pi, NM)
KX, KY = kmag * np.cos(kang), kmag * np.sin(kang)
PH = rng.uniform(0, 2 * math.pi, NM)
AMP = kmag ** (-5 / 6) * 0.9  # mais energia nas escalas grandes (inclinação tipo Kolmogorov)
AMP /= AMP.sum()


def envelope(x, y):
    """Intensidade da turbulência: zero antes do cilindro, cresce rio abaixo, concentrada na esteira que se abre."""
    d = np.clip((x - CX) / 900.0, 0, None)
    sigma = 40.0 + 140.0 * d
    return np.clip(d * 3.0, 0, 1.0) * np.exp(-((y - CY) ** 2) / (2 * sigma**2))


def vel(x, y):
    z = (x - CX) + 1j * (y - CY)
    r2 = np.abs(z) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        dw = U * (1 - A**2 / z**2)
    u, v = dw.real, -dw.imag
    # atrás do cilindro, o desenho é feito no referencial que anda com os vórtices (0,8 U):
    # é assim que a esteira aparece nas fotos de laboratório, com os laços fechados
    s = np.clip((x - CX - 50) / 160.0, 0, 1)
    u -= 0.8 * U * s * s * (3 - 2 * s)
    for vx, vy, g, rc in vort:
        dx, dy = x - vx, y - vy
        rr = dx * dx + dy * dy + 1e-9
        f = g / (2 * math.pi * rr) * (1 - np.exp(-rr / rc**2))
        u += -f * dy
        v += f * dx
    # psi = sum A sin(k.x + phi); u = dpsi/dy, v = -dpsi/dx
    ph = np.outer(x, KX) + np.outer(y, KY) + PH
    c = np.cos(ph) * AMP
    e = envelope(x, y) * 26.0
    u += e * (c @ KY)
    v += -e * (c @ KX)
    inside = r2 < A**2
    u[inside] = 0
    v[inside] = 0
    return u, v


def trace(x0, y0, steps, h):
    x, y = np.array(x0, float), np.array(y0, float)
    xs, ys = [x.copy()], [y.copy()]
    alive = np.ones_like(x, bool)
    for _ in range(steps):
        def f(px, py):
            u, v = vel(px, py)
            s = np.hypot(u, v) + 1e-9
            return u / s, v / s  # passo de comprimento fixo: linhas igualmente detalhadas
        k1 = f(x, y)
        k2 = f(x + h / 2 * k1[0], y + h / 2 * k1[1])
        k3 = f(x + h / 2 * k2[0], y + h / 2 * k2[1])
        k4 = f(x + h * k3[0], y + h * k3[1])
        nx = x + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        ny = y + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        out = (nx < -20) | (nx > W + 20) | (ny < -20) | (ny > H + 20) | ((nx - CX) ** 2 + (ny - CY) ** 2 < A**2)
        alive &= ~out
        x = np.where(alive, nx, x)
        y = np.where(alive, ny, y)
        xs.append(x.copy())
        ys.append(y.copy())
        if not alive.any():
            break
    return np.array(xs).T, np.array(ys).T


def poly(xs, ys):
    pts = []
    last = None
    for px, py in zip(xs, ys):
        if last is not None and abs(px - last[0]) < 0.05 and abs(py - last[1]) < 0.05:
            continue
        pts.append(f"{px:.1f},{py:.1f}")
        last = (px, py)
    return " ".join(pts)


paths = []
# linhas que entram pela esquerda, mais densas perto da altura do cilindro
ys0 = np.concatenate([np.linspace(-40, H + 40, 70), CY + rng.normal(0, 60, 50)])
xs, ys = trace(np.full_like(ys0, -15.0), ys0, 1400, 2.0)
for i in range(len(ys0)):
    near = abs(ys0[i] - CY) < 110
    paths.append((poly(xs[i], ys[i]), PAL["ink"] if near else PAL["soft"], 0.75 if near else 0.6, 0.85 if near else 0.6))

# laços dos vórtices: sementes em volta de cada núcleo, integradas por um trecho curto
for vx, vy, g, rc in vort:
    for rr in (0.35, 0.7, 1.05):
        n = 3
        ang = rng.uniform(0, 2 * math.pi, n)
        sx, sy = vx + rr * rc * np.cos(ang), vy + rr * rc * np.sin(ang)
        tx, ty = trace(sx, sy, 420, 1.6)
        for i in range(n):
            paths.append((poly(tx[i], ty[i]), PAL["soft"], 0.55, 0.7))

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       f'<rect width="{W}" height="{H}" fill="{PAL["bg"]}"/>',
       '<g fill="none" stroke-linecap="round" stroke-linejoin="round">']
for d, col, sw, op in paths:
    if d.count(" ") > 3:
        svg.append(f'<polyline points="{d}" stroke="{col}" stroke-width="{sw}" stroke-opacity="{op}"/>')
svg.append("</g>")

# cilindro com hachura
svg.append(f'<circle cx="{CX}" cy="{CY}" r="{A}" fill="{PAL["bg"]}" stroke="{PAL["ink"]}" stroke-width="1.1"/>')
svg.append(f'<clipPath id="c"><circle cx="{CX}" cy="{CY}" r="{A - 1}"/></clipPath><g clip-path="url(#c)" stroke="{PAL["faint"]}" stroke-width="0.7">')
for t in range(-80, 81, 7):
    svg.append(f'<line x1="{CX + t - 40}" y1="{CY + 40}" x2="{CX + t + 40}" y2="{CY - 40}"/>')
svg.append("</g>")

# anotações à mão
font = 'font-family="Architects Daughter"'
def text(x, y, s, size, col, extra=""):
    svg.append(f'<text x="{x}" y="{y}" {font} font-size="{size}" fill="{col}" {extra}>{s}</text>')

text(CX - 12, CY + A + 30, "D", 15, PAL["soft"])
svg.append(f'<path d="M{CX - A},{CY + A + 12} h{2 * A} M{CX - A},{CY + A + 6} v12 M{CX + A},{CY + A + 6} v12" stroke="{PAL["soft"]}" stroke-width="0.8"/>')
text(60, 120, "flow past a cylinder", 16, PAL["ink"])
text(60, 142, "Re ≈ 10⁴ · von Kármán street", 12, PAL["soft"])
svg.append(f'<path d="M60,150 q60,-3 150,1" stroke="{PAL["faint"]}" stroke-width="0.7" fill="none"/>')
text(60, 205, "U →", 15, PAL["soft"])
svg.append(f'<rect x="1300" y="610" width="30" height="92" fill="none" stroke="{PAL["faint"]}" stroke-width="0.7"/>')
text(1321, 690, "x230 · cfd", 11, PAL["faint"], 'transform="rotate(-90 1321 690)"')
text(1302, 728, "02", 16, PAL["soft"])
svg.append("</svg>")
print("\n".join(svg))
