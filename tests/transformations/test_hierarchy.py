from src.transformations import build_hierarchy, flatten_hierarchy


def test_hierarchy_builds_multiple_levels(sample_frame):
    tree = build_hierarchy(
        sample_frame,
        levels=["category", "subcategory", "product"],
        aggregations={"value": "sum", "quantity": "sum"},
    )
    assert [node["label"] for node in tree] == ["A", "B"]
    assert tree[0]["value"] == 30
    assert "_children" in tree[0]
    assert "_children" in tree[0]["_children"][0]
    assert tree[0]["node_id"] == "A"


def test_flatten_hierarchy_records_depth(sample_frame):
    tree = build_hierarchy(sample_frame, levels=["category", "subcategory"], aggregations={"value": "sum"})
    flat = flatten_hierarchy(tree)
    assert {row["depth"] for row in flat} == {0, 1}
    assert all("_children" not in row for row in flat)
