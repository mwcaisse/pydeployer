from pydeployer import get_project_name


def test_non_versioned_packages():
    project_name = get_project_name("HelloWorld.pydist", {})
    assert project_name == "helloworld"


def test_versioned_file_with_meta():
    project_name = get_project_name("PyDeployer-0.0.1-alpha.5.pydist", {
        "name": "PyDeployer"
    })
    assert project_name == "pydeployer"


def test_versioned_file_without_meta():
    project_name = get_project_name("PyDeployer-0.0.1-alpha.5.pydist", {})
    assert project_name == "pydeployer"


def test_versioned_file_without_meta_showreminder():
    project_name = get_project_name("ShowReminder-0.0.1-alpha.2.pydist", {})
    assert project_name == "showreminder"
