# Autocompletion

## bash

For Bash, add this to `~/.bashrc`:

~~~shell
eval "$(_CLOUDSCALE_COMPLETE=bash_source cloudscale)"
~~~

## zsh

For Zsh, add this to `~/.zshrc`:

~~~shell
eval "$(_CLOUDSCALE_COMPLETE=zsh_source cloudscale)"
~~~

## fish

For Fish, add this to `~/.config/fish/completions/cloudscale.fish`:

~~~shell
_CLOUDSCALE_COMPLETE=fish_source cloudscale | source
~~~
