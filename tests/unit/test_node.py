import logging
from unittest.mock import Mock

import pytest

from datachain.node import Node, NodeWithPath


@pytest.mark.parametrize("invalid_path", [["..", "outside.txt"], ["/outside.txt"]])
def test_instantiate_skips_invalid_destination_and_continues(
    invalid_path, tmp_path, caplog
):
    output = tmp_path / "output"
    client = Mock(uri="s3://source-bucket")
    invalid_node = NodeWithPath(Node(path="source.txt"), path=invalid_path)
    valid_node = NodeWithPath(Node(path="source.txt"), path=["safe.txt"])

    with caplog.at_level(logging.WARNING, logger="datachain"):
        invalid_node.instantiate(client, str(output), None)
        valid_node.instantiate(client, str(output), None)

    assert "invalid destination path" in caplog.text
    assert client.instantiate_object.call_count == 1
    file, destination, progress_bar, force = client.instantiate_object.call_args.args
    assert file.path == "source.txt"
    assert destination == str(output / "safe.txt")
    assert progress_bar is None
    assert force is False
    assert output.is_dir()
    assert not (tmp_path / "outside.txt").exists()
