---
title: "Fix a missing Codex remote model: restart the outdated app-server"
tags:
  - Codex
  - Linux
  - SSH
  - troubleshooting
---

GPT-6.1-Sol was available in my local Codex environment but missing from the
model picker for a remote project on `remote-ip`. The remote CLI had already
been upgraded, yet the desktop app was still connected to an older app-server
process that had survived the upgrade.

This post records the diagnosis and the procedure for restarting that remote
backend. The version numbers and PID below are observations from this case,
not values to reuse on another installation.

<!--more-->

## 1. Compare the installed and running versions

The checks produced the following results:

| Component | Observed result |
| --- | --- |
| Local app-server reported by the desktop app | `0.163.0-alpha.11` |
| Codex executable currently installed on the remote host | `0.163.0` |
| Remote app-server used by the desktop app | `0.158.0` |
| Model list returned by a separate instance of the installed remote executable | `gpt-6.1-sol` present and not hidden |

The remote configuration used a custom model provider and selected
`gpt-6-sol` as its default. Initially, either provider availability or a version
difference could have explained the missing entry. However, querying the new
remote executable through `model/list` returned:

```json
{
  "id": "gpt-6.1-sol",
  "model": "gpt-6.1-sol",
  "displayName": "GPT-6.1-Sol",
  "hidden": false,
  "isDefault": true
}
```

This established that the installed executable could list the model. It did
not test an actual model request or establish whether the provider would
accept that request.

## 2. Inspect the remote app-server process

Connect from the Mac terminal:

```bash
ssh remote-ip
```

List Codex app-server processes on the remote host:

```bash
ps -u "$(id -un)" -o pid,lstart,args | grep '[c]odex.*app-server'
```

In this installation, the output included a Node.js launcher, a native Codex
app-server, and a separate proxy. The native server command ended with:

```text
.../bin/codex -c features.code_mode_host=true app-server --listen unix://
```

Its PID was `153534`. The proxy instead ended with `app-server proxy`.
The process to inspect is the native server, not the proxy or
`codex-code-mode-host`.

On Linux, `/proc` allows checking the executable actually held by a running
process. Set the PID to the value from your own process listing:

```bash
server_pid=153534

readlink "/proc/$server_pid/exe"
"/proc/$server_pid/exe" --version
```

In this case, the executable link pointed into an old npm package directory
and ended with `(deleted)`. Running that executable through `/proc` returned:

```text
codex-cli 0.158.0
```

Meanwhile, the currently installed binary returned `codex-cli 0.163.0`.
The desktop connection log independently reported:

```text
Current reported app-server version: currentVersion=0.158.0 hostId=remote-ssh-discovered:remote-ip
```

An executable marked `(deleted)` can continue running on Linux because the
process still holds the old executable open. Replacing the files during an
upgrade does not automatically replace the code of that existing process.

## 3. Check the installed executable separately

In a remote interactive shell where Codex is on `PATH`, run:

```bash
command -v codex
codex --version
```

This only reports the version found through the shell's current `PATH`.
It does not report the version of an app-server that was started earlier.

My non-interactive SSH shell did not initially find `codex`, because Node.js
and Codex were installed through nvm. That was a shell environment issue,
not evidence that Codex was absent. The native executable in this installation
could be checked directly:

```bash
"$HOME/.nvm/versions/node/v24.18.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex" --version
```

The Node.js version and installation path are specific to this machine.
Use your actual executable path when comparing the installed version with
the one obtained through `/proc`.

## 4. Stop the old remote app-server

Wait for active Codex work on this host to finish. Stopping the shared remote
app-server interrupts the Codex chats connected to it.

Recheck the PID immediately before stopping it:

```bash
ps -p "$server_pid" -o pid,user,lstart,args
```

Confirm that this is still your native Codex process with
`app-server --listen unix://` in its arguments. Then request a normal exit:

```bash
kill -TERM "$server_pid"
```

The process belonged to my remote user, so `sudo` was unnecessary.
Start with `SIGTERM`; a forced `kill -9` is not the normal restart procedure.

## 5. Reconnect from the Codex desktop app

Return to the desktop app and allow it to reconnect. If the connection remains
disconnected, use the remote connection controls to reconnect `remote-ip`.
The desktop-managed connection should start or attach to the remote
app-server; there is no need to manually launch another standalone
`codex app-server` for this procedure.

Simply reopening a project or restarting the local desktop app may attach
to the same surviving remote process. The important step is replacing the
old remote backend.

After reconnecting, check:

1. The native server process has a new PID.
2. Its executable reports the expected installed version.
3. The remote project's model picker includes `GPT-6.1-Sol`.

For the process checks, repeat the listing and use the new native server PID:

```bash
ps -u "$(id -un)" -o pid,lstart,args | grep '[c]odex.*app-server'

# Replace NEW_PID with the native app-server PID from the listing.
server_pid=NEW_PID
"/proc/$server_pid/exe" --version
```

If the model appears but requests fail, investigate that error separately.
Model visibility alone does not verify provider routing, credentials, or
account access.

## 6. What was verified in this case

The diagnosis confirmed an installed `0.163.0` binary, a still-running
`0.158.0` remote app-server, and a model-list response from the new binary
that included `gpt-6.1-sol`. These findings identify the stale remote backend
as the concrete discrepancy behind the model-list investigation.

The investigation did not stop the existing shared server, and the
post-restart model picker and an actual GPT-6.1-Sol request had not yet been
verified when this procedure was written.

For similar problems after an upgrade, compare the executable on disk with
the process serving the desktop connection before reinstalling packages or
changing the model configuration.
