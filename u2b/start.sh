SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$SCRIPT_DIR/runtime"
nohup python3 -u "$SCRIPT_DIR/task_manager.py" > "$SCRIPT_DIR/runtime/task_work.log" 2>&1 &
ps -A
echo "🎉start success🎉"
