---
title: "Fix githubpage: Bundler cannot find Jekyll on macOS"
tags:
  - macOS
  - Ruby
  - Jekyll
  - troubleshooting
---

Running `githubpage` to preview my GitHub Pages site failed with:

```text
bundler: command not found: jekyll
Install missing gem executables with `bundle install`
```

The alias was correct, but the site's Ruby dependencies were missing. Installing
them also exposed an OpenSSL compatibility problem and slow network access.
This post records the working fix on my Apple Silicon Mac.

<!--more-->

## 1. Check the alias and active Ruby

Run these commands in an interactive zsh terminal:

```zsh
whence -v githubpage
which ruby bundle gem
ruby -v
```

My existing alias in `~/.zshrc` was:

```zsh
alias githubpage='bundle exec jekyll server'
```

It did not need to change. `bundle exec` runs Jekyll using the dependencies
selected for the current project's Gemfile; the alias does not install them.

The active interpreter was Homebrew Ruby 3.1.7, with executables under
`/opt/homebrew/opt/ruby@3.1/bin`. To use the same interpreter for the commands
below:

```zsh
export PATH="/opt/homebrew/opt/ruby@3.1/bin:$PATH"
```

This path is specific to this installation. Check your own Ruby path before
copying it to another machine.

## 2. Install the project's dependencies locally

The Gemfile uses `gemspec`, and the theme's gemspec declares Jekyll and its
plugins. Therefore, installing Jekyll alone is insufficient to reproduce the
project's complete dependency environment.

```zsh
bundle config set --local path vendor/bundle
bundle install
```

The first command saves the installation path in `.bundle/config`. Bundler
then installs the project's gems under `vendor/bundle` and records resolved
versions in `Gemfile.lock`. All three paths were already ignored by this
repository's `.gitignore`.

If installation succeeds, continue to the preview step. On this Mac, the
installation stalled, so I checked Ruby's HTTPS connection before retrying.

## 3. Diagnose and fix the Ruby HTTPS error

Although `curl` could reach RubyGems, Ruby's HTTPS client reported:

```text
certificate verify failed (unable to get certificate CRL)
```

I reproduced the failure independently of Bundler with a bounded request:

```zsh
ruby -rnet/http -e '
  uri = URI("https://index.rubygems.org/versions")
  Net::HTTP.start(uri.host, uri.port,
    use_ssl: true, open_timeout: 10, read_timeout: 10) do |http|
    puts http.head(uri.path).code
  end
'
```

To inspect the OpenSSL extension and linked library:

```zsh
ruby -ropenssl -e '
  puts "Ruby OpenSSL gem: #{OpenSSL::VERSION}"
  puts "Compiled with: #{OpenSSL::OPENSSL_VERSION}"
  puts "Loaded library: #{OpenSSL::OPENSSL_LIBRARY_VERSION}"
'
```

Before the fix, this environment used the default `openssl` gem 3.0.1,
compiled against OpenSSL 3.4.1, while loading Homebrew OpenSSL 3.6.0.
Updating the Ruby extension to version 3.3.2 resolved the observed certificate
error. This version supports Ruby 3.1; it is the version tested here, rather
than a recommendation to install whichever release is newest.

Because Ruby's own HTTPS requests were failing, I downloaded the gem with
`curl` and installed the local file:

```zsh
curl -fSL --connect-timeout 10 --max-time 60 \
  https://rubygems.org/gems/openssl-3.3.2.gem \
  -o /tmp/githubpage-openssl-3.3.2.gem

gem install --user-install --local /tmp/githubpage-openssl-3.3.2.gem \
  --no-document -- --with-openssl-dir=/opt/homebrew/opt/openssl@3
```

This installs the extension for the current user. Building it requires the
macOS compiler tools and the Homebrew OpenSSL headers, which were already
available on this machine.

Repeating the HTTPS check returned `200`, and `OpenSSL::VERSION` reported
`3.3.2`. Certificate verification remained enabled throughout the fix.

## 4. Use the configured HTTP proxy for downloads

Dependency downloads still stalled over the direct connection. My `~/.zshrc`
already provided the following alias:

```zsh
alias proxyon='export http_proxy=http://127.0.0.1:7897;export https_proxy=http://127.0.0.1:7897;'
```

After stopping the stalled installer with **Ctrl+C**, enable the proxy and
restart installation:

```zsh
proxyon
bundle install
```

For a shell where the alias is not loaded, use the equivalent commands:

```zsh
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
bundle install
```

The local proxy must be running on that port. The `http://` scheme in
`https_proxy` describes the proxy connection; the RubyGems destination still
uses HTTPS. These exports affect the current shell and its child processes.

The successful installation reported:

```text
Bundle complete! 4 Gemfile dependencies, 52 gems now installed.
Bundled gems are installed into `./vendor/bundle`
```

The resolved Jekyll version was 4.4.1.

## 5. Start and verify the preview

```zsh
bundle check
githubpage
```

The dependency check should print:

```text
The Gemfile's dependencies are satisfied
```

The server should finish generating the site and report:

```text
Server address: http://127.0.0.1:4000
Server running... press ctrl-c to stop.
```

Open [http://127.0.0.1:4000](http://127.0.0.1:4000) in a browser. To verify
the response from another terminal without sending localhost traffic through
a proxy:

```zsh
curl --noproxy '*' -sS -o /dev/null \
  -w 'HTTP status: %{http_code}\n' http://127.0.0.1:4000/
```

The repaired site returned HTTP `200` and the page title `Xinze Zhang`.
The theme emitted Sass division deprecation warnings, but the build completed
and the server worked. Those warnings are separate from the missing Jekyll
executable error.

For subsequent previews, the normal workflow is simply:

```zsh
githubpage
```

Keep that terminal running while browsing, and press **Ctrl+C** when finished.
The dependency installation and OpenSSL repair do not need to be repeated
for each preview.
