"""Regression tests for schema checks that could otherwise allow false passes."""

import unittest

from schema_check import validate


class SchemaCheckTests(unittest.TestCase):
    def test_booleans_are_not_numbers(self):
        self.assertTrue(validate(True, {"type": "integer"}))
        self.assertTrue(validate(True, {"const": 1}))
        self.assertTrue(validate({"v": True}, {"const": {"v": 1}}))
        self.assertFalse(validate([True, 1], {"uniqueItems": True}))

    def test_integral_numbers_and_uniqueness(self):
        self.assertFalse(validate(1.0, {"type": "integer"}))
        self.assertTrue(validate(1.5, {"type": "integer"}))
        self.assertTrue(validate([1, 1.0], {"uniqueItems": True}))
        self.assertTrue(validate([{"a": 1, "b": 2}, {"b": 2, "a": 1}], {"uniqueItems": True}))

    def test_closed_required_objects(self):
        schema = {"type": "object", "required": ["a"], "additionalProperties": False,
                  "properties": {"a": {"type": "string"}}}
        self.assertFalse(validate({"a": "ok"}, schema))
        self.assertTrue(validate({}, schema))
        self.assertTrue(validate({"a": "ok", "typo": 1}, schema))
        self.assertTrue(validate([], schema))

    def test_nested_reference(self):
        schema = {"$defs": {"entry": {"type": "integer", "minimum": 1}},
                  "type": "array", "items": {"$ref": "#/$defs/entry"}}
        self.assertFalse(validate([1], schema))
        self.assertTrue(validate([0], schema))

    def test_reference_siblings_apply(self):
        schema = {"$defs": {"integer": {"type": "integer"}},
                  "$ref": "#/$defs/integer", "minimum": 2}
        self.assertTrue(validate(1, schema))
        self.assertFalse(validate(2, schema))

    def test_alternatives(self):
        schema = {"anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}]}
        self.assertFalse(validate(None, schema))
        self.assertFalse(validate("fr-FR", schema))
        self.assertTrue(validate("", schema))
        self.assertTrue(validate(1, schema))

    def test_bounds_and_pattern(self):
        schema = {"type": "array", "minItems": 1, "maxItems": 2,
                  "items": {"type": "integer", "minimum": 0, "maximum": 255}}
        for value in ([], [256], [-1], [0, 0, 0]):
            self.assertTrue(validate(value, schema))
        self.assertFalse(validate([0, 255], schema))
        self.assertTrue(validate("ABC", {"pattern": "^[a-z]+$"}))

    def test_unsupported_constraints_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported schema keywords"):
            validate({}, {"properties": {"unused": {"oneOf": []}}})
        with self.assertRaisesRegex(ValueError, "only local"):
            validate({}, {"$ref": "https://example.invalid/schema"})

    def test_unanchored_patterns_use_json_schema_search_semantics(self):
        self.assertFalse(validate("apple", {"pattern": "p"}))
        self.assertTrue(validate("apple", {"pattern": "^p$"}))

    def test_dangling_references_are_reported_even_in_unused_properties(self):
        schema = {"properties": {"unused": {"$ref": "#/$defs/missing"}}}
        with self.assertRaisesRegex(ValueError, "unresolved schema reference"):
            validate({}, schema)
        with self.assertRaisesRegex(ValueError, "does not target a schema object"):
            validate({}, {"title": "not a schema", "$ref": "#/title"})

    def test_escaped_reference_tokens(self):
        schema = {"$defs": {"a/b~c": {"type": "integer"}}, "$ref": "#/$defs/a~1b~0c"}
        self.assertFalse(validate(1, schema))
        self.assertTrue(validate("1", schema))


if __name__ == "__main__":
    unittest.main()
