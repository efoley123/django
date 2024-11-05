import pytest
from unittest.mock import patch, MagicMock
from django.apps.registry import Apps, AppConfig
from django.core.exceptions import ImproperlyConfigured, AppRegistryNotReady


@pytest.fixture
def setup_apps():
    """
    Setup fixture for creating a new Apps instance with no installed apps.
    """
    return Apps(installed_apps=[])


# Test cases for normal, edge, and error scenarios

def test_apps_init_normal_case(setup_apps):
    """
    Ensure that the Apps instance initializes with the correct default values.
    """
    assert setup_apps.apps_ready is False
    assert setup_apps.models_ready is False
    assert setup_apps.ready is False


def test_apps_init_with_none_raises_runtime_error():
    """
    Verify that initializing Apps with None for installed_apps raises RuntimeError.
    """
    with pytest.raises(RuntimeError):
        Apps(installed_apps=None)


@patch('django.apps.registry.Apps.populate')
def test_populate_is_called_on_init_with_installed_apps(mock_populate):
    """
    Test that the populate method is called when Apps is initialized with non-empty installed_apps.
    """
    Apps(installed_apps=['app1', 'app2'])
    mock_populate.assert_called_once()


def test_populate_sets_ready_flags(setup_apps):
    """
    Check that calling populate sets the apps_ready, models_ready, and ready flags to True.
    """
    setup_apps.populate([])
    assert setup_apps.apps_ready is True
    assert setup_apps.models_ready is True
    assert setup_apps.ready is True


def test_populate_idempotent(setup_apps):
    """
    Ensure populate method is idempotent, meaning calling it more than once does not change the state.
    """
    setup_apps.populate([])
    first_state = (setup_apps.apps_ready, setup_apps.models_ready, setup_apps.ready)

    setup_apps.populate([])
    assert (setup_apps.apps_ready, setup_apps.models_ready, setup_apps.ready) == first_state


def test_populate_raises_improperly_configured_for_duplicate_app_labels(setup_apps):
    """
    Confirm populate raises ImproperlyConfigured when duplicate app labels are provided.
    """
    with pytest.raises(ImproperlyConfigured):
        setup_apps.populate(['app1', 'app1'])


def test_check_apps_ready_raises_app_registry_not_ready(setup_apps):
    """
    Verify check_apps_ready raises AppRegistryNotReady before populate is called.
    """
    with pytest.raises(AppRegistryNotReady):
        setup_apps.check_apps_ready()


def test_get_app_config_returns_correct_app_config(setup_apps):
    """
    Test get_app_config returns the correct AppConfig instance for a given label.
    """
    app_label = 'myapp'
    mock_app_config = MagicMock(spec=AppConfig)
    mock_app_config.label = app_label
    setup_apps.app_configs[app_label] = mock_app_config

    assert setup_apps.get_app_config(app_label) is mock_app_config


def test_get_app_config_raises_lookup_error_for_invalid_label(setup_apps):
    """
    Ensure get_app_config raises LookupError for an invalid app label.
    """
    with pytest.raises(LookupError):
        setup_apps.get_app_config('nonexistent')


@patch('django.apps.registry.apps.is_installed', return_value=False)
def test_is_installed_returns_false_for_non_installed_app(mock_is_installed, setup_apps):
    """
    Test is_installed method returns False for a non-installed app.
    """
    assert not setup_apps.is_installed('nonexistent_app')


@patch('django.apps.registry.apps.is_installed', return_value=True)
def test_is_installed_returns_true_for_installed_app(mock_is_installed, setup_apps):
    """
    Ensure is_installed method returns True for an installed app.
    """
    assert setup_apps.is_installed('existent_app')


def test_set_available_apps_updates_app_configs(setup_apps):
    """
    Test set_available_apps method updates app_configs correctly.
    """
    mock_app_config = MagicMock(spec=AppConfig)
    mock_app_config.name = 'myapp'
    setup_apps.app_configs['myapp'] = mock_app_config

    setup_apps.set_available_apps(['myapp'])
    assert 'myapp' in setup_apps.app_configs


def test_unset_available_apps_restores_app_configs(setup_apps):
    """
    Ensure unset_available_apps restores app_configs to its previous state.
    """
    original_app_configs = setup_apps.app_configs.copy()
    setup_apps.set_available_apps(['myapp'])
    setup_apps.unset_available_apps()
    assert setup_apps.app_configs == original_app_configs


@patch.object(Apps, 'populate')
def test_set_installed_apps_resets_and_populates(mock_populate, setup_apps):
    """
    Test set_installed_apps resets and populates apps.
    """
    setup_apps.set_installed_apps(['app1'])
    mock_populate.assert_called_once_with(['app1'])


def test_unset_installed_apps_restores_state(setup_apps):
    """
    Confirm unset_installed_apps restores the state before set_installed_apps was called.
    """
    original_state = (setup_apps.apps_ready, setup_apps.models_ready, setup_apps.ready)
    setup_apps.set_installed_apps(['app1'])
    setup_apps.unset_installed_apps()
    assert (setup_apps.apps_ready, setup_apps.models_ready, setup_apps.ready) == original_state