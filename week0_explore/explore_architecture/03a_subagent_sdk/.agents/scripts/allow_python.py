import sys
import json

def main():
    try:
        input_data = json.loads(sys.stdin.read())
        args = input_data.get("toolCall", {}).get("args", {})
        is_python = False
        for val in args.values():
            if isinstance(val, str) and ("python" in val.lower() or "python3" in val.lower()):
                is_python = True
                break
        
        # Check if the command runs python
        if is_python:
            # Auto-allow running python scripts in this workspace
            result = {
                "decision": "allow",
                "reason": "Auto-allowed running python command in workspace"
            }
            # Write to a log file to prove hook is executed
            try:
                with open('/Users/vivekmitra/.gemini/antigravity-cli/brain/3856ee49-635e-407b-b949-995c3be67f4e/scratch/hook_log.txt', 'a') as log_f:
                    log_f.write(f"Hook auto-allowed: {args}\n")
            except Exception:
                pass
        else:
            result = {
                "decision": "ask"
            }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({
            "decision": "ask",
            "reason": f"allow_python.py hook error: {str(e)}"
        }))

if __name__ == "__main__":
    main()
