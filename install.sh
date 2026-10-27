#!/usr/bin/env bash
# HHL seo-onpage installer. Run from the repo folder:  ./install.sh
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
echo "── checking tools"
for t in python3 node git ssh; do command -v $t >/dev/null || { echo "missing: $t (install it, then re-run)"; exit 1; }; done
echo "── python pieces"; python3 -m pip install --user --quiet beautifulsoup4
echo "── browser for checks (Playwright + Chromium, one time, ~150 MB)"
mkdir -p "$HOME/.seo-onpage/node"; (cd "$HOME/.seo-onpage/node" && npm init -y >/dev/null && npm install --silent playwright@1.48.2 && npx playwright install chromium >/dev/null)
echo "── linking the skill into Claude Code"
mkdir -p "$HOME/.claude/skills"; ln -sfn "$KIT/skill/seo-onpage" "$HOME/.claude/skills/seo-onpage"
echo "── the seo command"
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/seo" <<SH
#!/usr/bin/env bash
export PLAYWRIGHT="\$HOME/.seo-onpage/node/node_modules/playwright"
[ -f "\$HOME/.seo-onpage/keys.env" ] && source "\$HOME/.seo-onpage/keys.env"
exec python3 "$KIT/skill/seo-onpage/scripts/seo.py" "\$@"
SH
chmod +x "$HOME/.local/bin/seo"
grep -q '.local/bin' "$HOME/.zshrc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
[ -f "$HOME/.seo-onpage/sites.json" ] || echo '{}' > "$HOME/.seo-onpage/sites.json"
echo
echo "Done. Open a new terminal, start Claude Code (claude), and type:  /seo-onpage"
echo "Then say: what do I do first?"
