# Xinze Zhang's personal website

This repository contains the source of [xinzezhang.github.io](https://xinzezhang.github.io), built with Jekyll and the [TeXt theme](https://github.com/kitian616/jekyll-TeXt-theme). The theme's MIT license is retained in [LICENSE](LICENSE).

## Local preview

Install the Ruby dependencies with `bundle install`, then run:

```sh
bundle exec jekyll serve
```

Open <http://127.0.0.1:4000/>. Site-wide changes to `_config.yml` require restarting the server.

## Site content

- `about-zh.md` and `about.md`: Chinese and English profiles, publications, projects, teaching, and honors.
- `_posts/`: personal blog posts; `index.html` lists the posts and `archive.html` provides the archive.
- `_data/navigation.yml`: site navigation and the Chinese profile sidebar.
- `_layouts/`, `_includes/`, `_sass/`, and `assets/`: the local TeXt theme used to build the site.
- `images/`: site images.
- `_pub_ed/`, `_pub_ur/`, and `_pub_wo/`: historical publication records, currently not configured as output collections.
- `tools/add_paper.py`: helper for adding a paper to the Chinese profile; run with `--help` for usage.

The published site is generated from the repository root using `_config.yml`. Generated `_site/` content, local Bundler dependencies, and caches are not source files.
