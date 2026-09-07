"""Dependency-free checker for the JSON Schema subset used by repository contracts.

This validates documents, not consumer implementations. Unsupported schema keywords fail
closed so a new constraint cannot silently disappear from repository validation.
"""

import re


KEYWORDS = {
    "$schema", "$id", "$defs", "$ref", "title", "description", "type", "properties",
    "additionalProperties", "required", "items", "minItems", "maxItems", "uniqueItems",
    "minLength", "pattern", "minimum", "maximum", "enum", "const", "anyOf",
}


def check_schema(schema):
    if not isinstance(schema, dict):
        raise ValueError("schemas must be objects")
    unknown = set(schema) - KEYWORDS
    if unknown:
        raise ValueError(f"unsupported schema keywords: {sorted(unknown)}")
    for key in ("properties", "$defs"):
        for child in schema.get(key, {}).values():
            check_schema(child)
    if "items" in schema:
        check_schema(schema["items"])
    for child in schema.get("anyOf", []):
        check_schema(child)


def equal(left, right):
    # JSON booleans are not numbers; Python's True == 1 is not schema equality.
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(equal(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(equal(a, b) for a, b in zip(left, right))
    return left == right


def errors(value, schema, root=None, path="$"):
    root = schema if root is None else root
    result = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise ValueError(f"only local schema references are supported: {ref}")
        target = root
        for part in ref[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        result.extend(errors(value, target, root, path))
    if "anyOf" in schema and not any(
        not errors(value, child, root, path) for child in schema["anyOf"]
    ):
        result.append(f"{path}: no anyOf alternative matches")
    kind = schema.get("type")
    types = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "boolean": isinstance(value, bool),
        "null": value is None,
        "integer": (isinstance(value, (int, float)) and not isinstance(value, bool)
                    and value == int(value)),
    }
    if kind is not None and kind not in types:
        raise ValueError(f"unsupported schema type: {kind}")
    if kind is not None and not types[kind]:
        return result + [f"{path}: expected {kind}"]
    if "const" in schema and not equal(value, schema["const"]):
        result.append(f"{path}: incorrect constant")
    if "enum" in schema and not any(equal(value, item) for item in schema["enum"]):
        result.append(f"{path}: outside enum")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                result.append(f"{path}: missing {key}")
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys():
                result.append(f"{path}: unknown {key}")
        for key in value.keys() & properties.keys():
            result.extend(errors(value[key], properties[key], root, f"{path}.{key}"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            result.append(f"{path}: too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            result.append(f"{path}: too many items")
        if schema.get("uniqueItems") and any(
            equal(item, earlier) for index, item in enumerate(value) for earlier in value[:index]
        ):
            result.append(f"{path}: duplicate item")
        if "items" in schema:
            for index, item in enumerate(value):
                result.extend(errors(item, schema["items"], root, f"{path}[{index}]"))
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            result.append(f"{path}: string too short")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            result.append(f"{path}: pattern mismatch")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            result.append(f"{path}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            result.append(f"{path}: above maximum")
    return result


def validate(value, schema):
    check_schema(schema)
    return errors(value, schema)
