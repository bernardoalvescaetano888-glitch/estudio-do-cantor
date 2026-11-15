# 🚀 DEPLOY — Publicar no GitHub e gerar downloads p/ Windows, Mac e Linux

## 1. Criar o repositório e enviar o código

```bash
cd estudio-do-cantor
git init
git add .
git commit -m "Estúdio do Cantor v1.0.0"
git branch -M main
# Crie o repositório vazio em github.com/new (sem README), depois:
git remote add origin https://github.com/SEU-USUARIO/estudio-do-cantor.git
git push -u origin main
```

> Com a CLI do GitHub instalada e logada, dá pra fazer tudo:
> ```bash
> gh repo create estudio-do-cantor --public --source=. --push
> ```

## 2. Gerar downloads para os 3 sistemas

O arquivo `.github/workflows/build.yml` já está pronto. **Toda vez que você criar uma tag de versão, o GitHub Actions compila automaticamente o app para Windows, macOS e Linux:**

```bash
git tag v1.0.0
git push origin v1.0.0
```

Aguarde ~15–25 min → os executáveis aparecem em:
`github.com/SEU-USUARIO/estudio-do-cantor/releases`

| Sistema | Artefato |
|---|---|
| Windows | `EstudioDoCantor.exe` (onefile) |
| macOS | `EstudioDoCantor` (binário; abrir com botão direito → Abrir, pois não é assinado) |
| Linux | `EstudioDoCantor` (binário) |

Também ficam disponíveis como **artifacts** em `Actions` (para testar antes de liberar).

## 3. Checklist do vendedor

- [ ] Trocar `STORE_URL` no `app.py` pelo link real de pagamento
- [ ] Trocar o `SECRET` em `lic_core.py` por uma frase secreta SUA (chaves antigas deixam de valer)
- [ ] Testar `python keygen.py -t 1 -m 1` e ativar no app
- [ ] Fazer 1 release de teste (tag) e baixar os 3 artefatos
- [ ] Gravar um vídeo de 30s mostrando a separação de voz → postar em Reels/TikTok/YouTube

## 4. Dicas de build

- O build roda em `windows-latest`, `macos-latest` e `ubuntu-latest` (Python 3.10, PyTorch CPU).
- O executável não inclui o **FFmpeg** — instrua o usuário a instalá-lo (ou embuta o binário na v2 e remova a checagem).
- Para AppImage/deb no Linux, adicione no workflow uma etapa extra com `linuxdeploy`/`dpkg` (opcional).
- macOS sem assinatura: o usuário precisa clicar com o **botão direito → Abrir** na 1ª execução.
