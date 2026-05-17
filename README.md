# Guia de Instalação do Docker

Documentação oficial: https://docs.docker.com

---

## Linux (Ubuntu, Debian, Fedora e derivados)

A forma mais simples é usar o script oficial de conveniência mantido pela Docker. Ele detecta a distribuição e configura os repositórios automaticamente.

### 1. Baixar e executar o script

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2. Adicionar seu usuário ao grupo docker

Sem isso, todo comando vai exigir `sudo`. Não recomendado.

```bash
sudo usermod -aG docker $USER
```

### 3. Aplicar a alteração de grupo

Feche e abra o terminal, ou faça logout e login no sistema.

### 4. Validar a instalação

```bash
docker version
docker info
docker run hello-world
```

O comando `docker version` deve mostrar duas seções: **Client** e **Server**. Se aparecer só Client, o daemon não está rodando. Inicie com:

```bash
sudo systemctl start docker
sudo systemctl enable docker   # opcional, para iniciar no boot
```

---

## Windows

Documentação oficial: https://docs.docker.com/desktop/setup/install/windows-install/

Pré-requisito: WSL2 ativo. Verificar com `wsl --status` no PowerShell.

---

## macOS

Documentação oficial: https://docs.docker.com/desktop/setup/install/mac-install/

Escolha a versão correta do instalador: Apple Silicon (M1, M2, M3) ou Intel.

---

## Plano B

Caso a instalação local não funcione, use o lab gratuito no navegador:

https://labs.play-with-docker.com
