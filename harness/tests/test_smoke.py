from harness import main


def test_main_runs(capsys):
    main()
    assert "harness" in capsys.readouterr().out
