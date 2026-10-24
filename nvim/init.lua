-- graphite · neovim: o tema "quiet" (monocromático, vem com o neovim) e o mínimo de interface
vim.opt.termguicolors = true
vim.opt.number = true
vim.opt.relativenumber = false
vim.opt.signcolumn = "no"
vim.opt.laststatus = 0
vim.opt.ruler = true
vim.opt.cursorline = false
vim.opt.wrap = false
vim.opt.expandtab = true
vim.opt.shiftwidth = 2
vim.opt.tabstop = 2
vim.opt.scrolloff = 6
vim.opt.fillchars = { eob = " " }

local function sync_bg()
  local f = io.open(vim.fn.expand("~/.cache/theme"))
  local mode = f and f:read("*l") or "dark"
  if f then f:close() end
  vim.o.background = mode
  vim.cmd.colorscheme("quiet")
  if mode == "dark" then
    vim.api.nvim_set_hl(0, "Normal", { bg = "NONE", fg = "#d0d1d2" })
    vim.api.nvim_set_hl(0, "LineNr", { fg = "#5c5f63" })
    vim.api.nvim_set_hl(0, "Comment", { fg = "#8b8e92", italic = true })
  else
    vim.api.nvim_set_hl(0, "Normal", { bg = "NONE", fg = "#2f3134" })
    vim.api.nvim_set_hl(0, "LineNr", { fg = "#a9aaa8" })
    vim.api.nvim_set_hl(0, "Comment", { fg = "#5e6064", italic = true })
  end
end
sync_bg()
vim.api.nvim_create_autocmd("FocusGained", { callback = sync_bg })
