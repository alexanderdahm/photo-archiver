from media_archiver.cli import parse_args


def test_parse_args_requires_config():
    args = parse_args(["--config", "config.yaml"])
    assert args.config == "config.yaml"
    assert args.apply is False


def test_parse_args_apply_flag():
    args = parse_args(["--config", "config.yaml", "--apply"])
    assert args.apply is True
