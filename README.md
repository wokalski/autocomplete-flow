
## Autocomplete-flow

Flow autocompletion for [deoplete](https://github.com/Shougo/deoplete.nvim)

- ✅ [flowbin](https://www.npmjs.com/package/flow-bin) support
- ✅ always async
- ✅ supports function argument completion with [neosnippet](https://github.com/Shougo/neosnippet.vim)

## Installation

This plugin requires neovim (vim8 should work, too) with python.
Minimal working `.vimrc`/`init.vim`:

```vimL
call plug#begin()
  Plug 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }
  Plug 'wokalski/autocomplete-flow'
  " For func argument completion
  Plug 'Shougo/neosnippet'
  Plug 'Shougo/neosnippet-snippets'
call plug#end()

" deoplete

let g:deoplete#enable_at_startup = 1

" neosnippet
        
let g:neosnippet#enable_completed_snippet = 1

```

## Configuration

If neosnippet integration is not enabled, this plugin will insert an opening
paren when completing a function name.
Add this line to your configuration to disable that behavior:

```vimL
let g:autocomplete_flow#insert_paren_after_function = 0
```

## Credits

The initial version is based on [autocomplete-swift](https://github.com/mitsuse/autocomplete-swift). Thanks to @SeeThruHead for the vim script to find flow-bin.

