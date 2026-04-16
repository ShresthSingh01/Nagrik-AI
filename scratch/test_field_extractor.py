"""Quick test for field extraction fixes."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.field_extractor import extract_fields_from_markdown

# Test 1: Markdown-formatted labels (was BROKEN before fix)
md1 = """**Name**: ________
**Father's Name**: Ram Kumar
**Address**: ________
**Mobile Number**: 9876543210
"""
fields1 = extract_fields_from_markdown(md1)
print(f"Test 1 (bold markdown labels): {len(fields1)} fields")
for f in fields1:
    print(f"  - {f['label']} ({f['pattern_type']})")
assert len(fields1) >= 3, f"FAIL: Expected >= 3 fields, got {len(fields1)}"
print("  PASS\n")

# Test 2: Hindi labels with colons
md2 = """नाम: ________
पिता का नाम: ________
पता: ________
मोबाइल नंबर: 9876543210
आधार संख्या: ____________
"""
fields2 = extract_fields_from_markdown(md2)
print(f"Test 2 (Hindi labels): {len(fields2)} fields")
for f in fields2:
    print(f"  - {f['label']} ({f['pattern_type']})")
assert len(fields2) >= 4, f"FAIL: Expected >= 4 fields, got {len(fields2)}"
print("  PASS\n")

# Test 3: Table-based fields
md3 = """| Field | Value |
| --- | --- |
| Name | John Doe |
| Phone | 9876543210 |
| Address | 123 Street |
"""
fields3 = extract_fields_from_markdown(md3)
print(f"Test 3 (table fields): {len(fields3)} fields")
for f in fields3:
    print(f"  - {f['label']} ({f['pattern_type']})")
assert len(fields3) >= 2, f"FAIL: Expected >= 2 fields, got {len(fields3)}"
print("  PASS\n")

# Test 4: Heading-formatted labels (OCR often does this)
md4 = """# Application Form
## Name: ________
## Father's Name: Shyam Kumar
## Date of Birth: __/__/____
"""
fields4 = extract_fields_from_markdown(md4)
print(f"Test 4 (heading-formatted labels): {len(fields4)} fields")
for f in fields4:
    print(f"  - {f['label']} ({f['pattern_type']})")
assert len(fields4) >= 2, f"FAIL: Expected >= 2 fields, got {len(fields4)}"
print("  PASS\n")

# Test 5: Checkbox fields
md5 = """[ ] Male
[x] Female
[ ] Other
"""
fields5 = extract_fields_from_markdown(md5)
print(f"Test 5 (checkboxes): {len(fields5)} fields")
for f in fields5:
    print(f"  - {f['label']} ({f['pattern_type']})")
assert len(fields5) >= 3, f"FAIL: Expected >= 3 fields, got {len(fields5)}"
print("  PASS\n")

# Test 6: Standalone label followed by blank line
md6 = """Applicant Name

Date of Birth
___________
District

Village
---
"""
fields6 = extract_fields_from_markdown(md6)
print(f"Test 6 (standalone labels + blank lines): {len(fields6)} fields")
for f in fields6:
    print(f"  - {f['label']} ({f['pattern_type']})")
assert len(fields6) >= 2, f"FAIL: Expected >= 2 fields, got {len(fields6)}"
print("  PASS\n")

print("=" * 50)
print("ALL TESTS PASSED!")
