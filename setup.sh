#!/usr/bin/env bash
# ============================================================
# RunBot 一键环境初始化脚本
# 用法：source setup.sh  （推荐，激活虚拟环境）
#       bash setup.sh    （也可以，但需要手动 activate）
# ============================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'
VENV_DIR=".venv"
_SETUP_OK=1

info()  { echo -e "${GREEN}[RunBot]${NC} $1"; }
warn()  { echo -e "${YELLOW}[RunBot]${NC} $1"; }
fail()  { echo -e "${RED}[RunBot]${NC} $1"; _SETUP_OK=0; }

# ---- 1. 检测 Python >=3.10 ----
info "检测 Python 环境..."
PYTHON_CMD=""
# 搜索 PATH 中的 python3/python，以及 macOS 常见安装路径
_CANDIDATES="python3 python"
for v in 3.13 3.12 3.11 3.10; do
    _CANDIDATES="$_CANDIDATES /Library/Frameworks/Python.framework/Versions/$v/bin/python3"
    _CANDIDATES="$_CANDIDATES /usr/local/bin/python$v"
    _CANDIDATES="$_CANDIDATES /opt/homebrew/bin/python$v"
done

for cmd in $_CANDIDATES; do
    if command -v "$cmd" &>/dev/null || [ -x "$cmd" ]; then
        ver=$("$cmd" -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}')" 2>/dev/null || true)
        if [ -n "$ver" ]; then
            major=${ver%%.*}
            minor=${ver##*.}
            if [ "$major" -ge 3 ] 2>/dev/null && [ "$minor" -ge 10 ] 2>/dev/null; then
                PYTHON_CMD="$cmd"
                break
            fi
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    fail "未找到 Python >= 3.10，请先安装 Python 3.10+"
fi

# 如果 Python 检测失败，提前退出
if [ "$_SETUP_OK" -eq 0 ]; then
    return 2>/dev/null; exit 1
fi

info "使用 Python: $($PYTHON_CMD --version) ($(command -v $PYTHON_CMD))"

# ---- 2. 创建虚拟环境 ----
if [ -d "$VENV_DIR" ]; then
    info "虚拟环境已存在：${VENV_DIR}/"
else
    info "创建虚拟环境：${VENV_DIR}/"
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        fail "虚拟环境创建失败"
        return 2>/dev/null; exit 1
    fi
fi

# ---- 3. 激活虚拟环境 ----
source "${VENV_DIR}/bin/activate"
info "虚拟环境已激活"

# ---- 4. 升级 pip ----
info "升级 pip..."
pip install --upgrade pip -q 2>/dev/null
if [ $? -ne 0 ]; then
    fail "pip 升级失败"
    return 2>/dev/null; exit 1
fi

# ---- 5. 安装依赖 ----
info "安装项目依赖..."
pip install -r requirements.txt -q 2>/dev/null
if [ $? -ne 0 ]; then
    fail "依赖安装失败，请检查 requirements.txt"
    return 2>/dev/null; exit 1
fi

# ---- 6. 安装项目（editable 模式，注册 rbot 命令）----
info "安装 RunBot（editable 模式）..."
pip install -e . -q 2>/dev/null
if [ $? -ne 0 ]; then
    fail "RunBot 安装失败，请检查 pyproject.toml"
    return 2>/dev/null; exit 1
fi

# ---- 7. 验证 rbot 命令 ----
if command -v rbot &>/dev/null; then
    info "rbot 命令已就绪：$(rbot --version 2>&1)"
else
    fail "rbot 命令安装失败，请检查 pyproject.toml 和 requirements.txt"
    return 2>/dev/null; exit 1
fi

# ---- 8. 创建必要目录 ----
mkdir -p logs reports database

# ---- 9. 检查 allure 命令行（可选）----
if ! command -v allure &>/dev/null; then
    warn "未安装 allure 命令行（可选），如需 allure 报告请执行："
    warn "  brew install allure  (macOS)"
    warn "  框架自带 HTML 报告（reports/runbot.html），不装也能用"
fi

# ---- 9. 检查配置文件 ----
if [ ! -f "conf/config.yaml" ]; then
    warn "未找到 conf/config.yaml，创建示例配置..."
    mkdir -p conf
    cat > conf/config.yaml << 'EOF'
current_env: test

test:
  host: https://httpbin.org
  account:
    user: test_user
    pwd: '123456'

staging:
  host: https://stagingapi.example.com
  account:
    user: staging_user
    pwd: '123456'
EOF
    info "已创建示例配置：conf/config.yaml"
fi

# ---- 10. 完成 ----
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  RunBot 环境初始化完成${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  虚拟环境已激活，可直接使用。"
echo ""
echo "  常用命令："
echo "    rbot run                  # 运行全部用例"
echo "    rbot run -m member        # 按 mark 运行"
echo "    rbot run -e staging       # 切换环境"
echo "    rbot gen -s <spec> -o <output>  # 代码生成"
echo "    rbot ai --api <file> --output <dir>  # AI 生成用例"
echo ""
