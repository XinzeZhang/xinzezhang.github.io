---
title: Ollama model storage, server address, and model renaming

tags:
    -linux
    -ollama
    -python
---


This guide configures Ollama to use the following defaults:

```text
Model directory: /nvmedata/ollama/models
Server address:  0.0.0.0:11434
Service user:    ollama
```

It also explains how to migrate models from Ollama's default system location
and rename a model without duplicating its underlying model blobs.

## 1. Use a persistent systemd override

Do not rely on editing `/etc/systemd/system/ollama.service` directly. An
Ollama installer or update can replace that unit file and remove custom
environment variables.

Instead, create a systemd drop-in, which is normally preserved when the main
unit is replaced:

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d

printf '%s\n' \
  '[Service]' \
  'Environment="OLLAMA_MODELS=/nvmedata/ollama/models"' \
  'Environment="OLLAMA_HOST=0.0.0.0:11434"' \
  | sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null

sudo chmod 0644 /etc/systemd/system/ollama.service.d/override.conf
```

The resulting file should be:

```ini
[Service]
Environment="OLLAMA_MODELS=/nvmedata/ollama/models"
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Prepare the model directory with ownership matching the Ollama service:

```bash
sudo install -d -o ollama -g ollama -m 0755 /nvmedata/ollama/models
sudo chown -R ollama:ollama /nvmedata/ollama
```

Reload systemd and restart Ollama:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama.service
```

## 2. Verify the effective configuration

Inspect the complete unit, including drop-ins:

```bash
systemctl cat ollama.service
```

Inspect the effective environment and drop-in path:

```bash
systemctl show ollama.service \
  -p ActiveState \
  -p SubState \
  -p Environment \
  -p DropInPaths
```

The output should contain:

```text
ActiveState=active
SubState=running
OLLAMA_MODELS=/nvmedata/ollama/models
OLLAMA_HOST=0.0.0.0:11434
DropInPaths=.../ollama.service.d/override.conf
```

Verify the listening address:

```bash
ss -ltnp | grep ':11434'
```

Verify model visibility:

```bash
ollama list
```

## 3. Migrate models from the old default directory

The system-service default is commonly:

```text
/usr/share/ollama/.ollama/models
```

Stop Ollama before migrating files so that downloads and manifest updates do
not occur during the copy:

```bash
sudo systemctl stop ollama.service
```

Merge the old store into the NVMe store. `--ignore-existing` avoids rewriting
content-addressed blobs already present at the destination:

```bash
sudo rsync -aH --ignore-existing \
  /usr/share/ollama/.ollama/models/ \
  /nvmedata/ollama/models/

sudo chown -R ollama:ollama /nvmedata/ollama
```

Make sure the persistent override from section 1 exists, then restart Ollama:

```bash
sudo systemctl daemon-reload
sudo systemctl start ollama.service
ollama list
```

Do not delete the old store until all expected models appear in `ollama list`
and at least one migrated model passes `ollama show`:

```bash
ollama show MODEL_NAME
```

After successful verification, remove only the exact old model directory:

```bash
sudo rm -rf /usr/share/ollama/.ollama/models
sudo install -d -o ollama -g ollama -m 0755 \
  /usr/share/ollama/.ollama/models
```

The empty directory is recreated for compatibility, but the service continues
to use `/nvmedata/ollama/models`.

## 4. Check the configuration after an Ollama update

After updating Ollama, run:

```bash
systemctl show ollama.service -p Environment -p DropInPaths
ollama list
```

If the drop-in is listed and the two environment variables are present, no
manual reconfiguration is needed. If necessary, reload the service manager:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama.service
```

## 5. Rename an Ollama model

Ollama does not provide an in-place `rename` command. The safe equivalent is:

1. Copy the manifest to the desired name.
2. Confirm both names have the same model ID.
3. Remove the old manifest name.

For example:

```bash
old_name='modelscope.cn/unsloth/gemma-4-26B-A4B-it-GGUF:latest'
new_name='gemma-4-26B-A4B:latest'

ollama cp "$old_name" "$new_name"
ollama list
ollama show "$new_name"
```

Confirm that the old and new entries in `ollama list` have the same ID. Then
remove the old name:

```bash
ollama rm "$old_name"
ollama list
```

`ollama cp` normally creates another manifest reference to the same
content-addressed blobs. It does not duplicate the full model weights.

The renamed model can then be run without writing the `:latest` tag:

```bash
ollama run gemma-4-26B-A4B
```

## 6. Remote-access security note

`OLLAMA_HOST=0.0.0.0:11434` exposes Ollama on every network interface. Ollama's
API should not be exposed directly to the public Internet. Restrict port 11434
with the host firewall, a private network, VPN, or authenticated reverse proxy.

To allow only local clients instead, use:

```ini
Environment="OLLAMA_HOST=127.0.0.1:11434"
```

After changing the address, reload and restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama.service
```

