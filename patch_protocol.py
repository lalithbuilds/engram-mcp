import re
import os

with open("server.py", "r") as f:
    code = f.read()

# 1. Fix MCP Router (params: null hang, and notification tools/call side-effects)
handle_old = """def handle(msg):
    method = msg.get("method", "")
    mid_ = msg.get("id")
    if method == "initialize":"""
    
handle_new = """def handle(msg):
    method = msg.get("method", "")
    mid_ = msg.get("id")
    
    # Spec violation fix: Ignore tool calls sent as notifications (no id)
    if "id" not in msg and method.startswith("tools/"):
        return None

    if method == "initialize":"""
code = code.replace(handle_old, handle_new)

# Fix params: null hang
call_old = """    elif method == "tools/call":
        p = msg.get("params", {})
        tn = p.get("name", "")
        ta = p.get("arguments", {})
        if ta is None:
            ta = {}"""
            
call_new = """    elif method == "tools/call":
        p = msg.get("params") or {}
        tn = p.get("name", "")
        ta = p.get("arguments") or {}"""
code = code.replace(call_old, call_new)

# Fix Prompt Injection (Wrap context in XML tags)
# In t_auto_context and t_smart_search, the output is JSON.
# Wait, the user said "memories are injected verbatim into boot context - no delimiters".
# Let's check where memories are returned as raw strings.
# Mostly they are returned as JSON arrays of objects. 
# But let's wrap the `content` field in <memory> tags? No, returning JSON is standard. 
# Wait, t_auto_context returns a single string of formatted memories! Let's check t_auto_context.
