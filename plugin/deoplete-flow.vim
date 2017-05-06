if exists('g:loaded_autocomplete_flow')
  finish
endif

let g:loaded_autocomplete_flow = 1

"Use locally installed flow from https://github.com/flowtype/vim-flow/issues/24
let local_flow = finddir('node_modules', '.;') . '/.bin/flow'
if matchstr(local_flow, "^\/\\w") == ''
    let local_flow= getcwd() . "/" . local_flow
endif
if executable(local_flow)
  let g:autocomplete_flow#flowbin = local_flow
else
  let g:autocomplete_flow#flowbin = 'flow'
endif

" If the user does not use neosnippet, insert a paren when completing a function
" name by default
if !exists("g:autocomplete_flow#insert_paren_after_function")
  let g:autocomplete_flow#insert_paren_after_function = 1
endif
