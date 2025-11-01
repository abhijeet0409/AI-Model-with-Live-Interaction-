# inspect_livekit.py
"""
Utility to inspect the LiveKit Python SDK (livekit.api) to determine
the correct class names, signatures, and available methods.

Useful for debugging token generation issues (401 Unauthorized / Invalid grant).
"""

import inspect
import livekit.api as api

print("=" * 80)
print("🔍 Inspecting LiveKit Python SDK (livekit.api)")
print("=" * 80)

# ---------------------------------------------------------------------
# AccessToken details
# ---------------------------------------------------------------------
print("\n=== AccessToken class ===")
try:
    sig = inspect.signature(api.AccessToken)
    print("Signature:", sig)
except Exception as e:
    print("ERROR reading AccessToken signature:", e)

try:
    print("\nDocstring:")
    print(api.AccessToken.__doc__ or "(no docstring)")
except Exception as e:
    print("ERROR reading AccessToken docstring:", e)

# ---------------------------------------------------------------------
# Grant classes (different SDK versions may use different names)
# ---------------------------------------------------------------------
print("\n=== Checking for Grant-related classes ===")
candidates = ["VideoGrant", "VideoGrants", "RoomGrant", "ParticipantGrant"]
found_any = False

for cname in candidates:
    if hasattr(api, cname):
        found_any = True
        cls = getattr(api, cname)
        print(f"\n✅ Found class: {cname}")
        try:
            print("Signature:", inspect.signature(cls))
        except Exception as e:
            print("ERROR reading signature:", e)
        try:
            doc = inspect.getdoc(cls)
            print("Docstring (first line):", doc.splitlines()[0] if doc else "(no docstring)")
        except Exception as e:
            print("ERROR reading docstring:", e)

if not found_any:
    print("⚠️ No Grant classes found (check your livekit SDK version).")

# ---------------------------------------------------------------------
# Utility: List all attributes of api module
# ---------------------------------------------------------------------
print("\n=== All public members of livekit.api ===")
for name in sorted([n for n in dir(api) if not n.startswith("_")]):
    print("-", name)

print("\n✅ Inspection complete.")
print("=" * 80)
