import pytest
from unittest.mock import patch, MagicMock
from django.apps.registry import Apps
from django.core.exceptions import ImproperlyConfigured, AppRegistryNotReady

# Setup for all tests, if necessary
@pytest.fixture
def setup_apps():
    return Apps(installed_apps=[])

def test_apps_init_normal_case(setup_apps):
    """
    Test that Apps initializes correctly with empty list.
    """
    assert setup_apps.apps_ready == False
    assert setup_apps.models_ready == False
    assert setup_apps.ready == False

def test_apps_init_with_none_raises_runtime_error():
    """
    Test that initializing Apps with None raises RuntimeError.
    """
    with pytest.raises(RuntimeError):
        Apps(installed_apps=None)

@patch('django.apps.registry.Apps.populate')
def test_populate_is_called(mock_populate, setup_apps):
    """
    Test that populate is called upon initialization with non-None installed_apps.
    """
    Apps(installed_apps=['app1', 'app2'])
    mock_populate.assert_called_once_with(['app1', 'app2'])

def test_populate_sets_ready_flags(setup_apps):
    """
    Test that populate sets apps_ready, models_ready, and ready flags to True.
    """
    setup_apps.populate(installed_apps=[])
    assert setup_apps.apps_ready == True
    assert setup_apps.models_ready == True
    assert setup_apps.ready == True

def test_populate_idempotent(setup_apps):
    """
    Test that calling populate more than once has no effect beyond the first call.
    """
    setup_apps.populate(installed_apps=[])
    initial_ready_state = (setup_apps.apps_ready, setup_apps.models_ready, setup_apps.ready)

    setup_apps.populate(installed_apps=[])
    assert (setup_apps.apps_ready, setup_apps.models_ready, setup_apps.ready) == initial_ready_state

def test_populate_raises_improperly_configured_for_duplicate_app_labels(setup_apps):
    """
    Test that populate raises ImproperlyConfigured when duplicate app labels are provided.
    """
    with pytest.raises(ImproperlyConfigured):
        setup_apps.populate(installed_apps=['app1', 'app1'])

def test_check_apps_ready_raises_app_registry_not_ready(setup_apps):
    """
    Test that check_apps_ready raises AppRegistryNotReady before populate is called.
    """
    with pytest.raises(AppRegistryNotReady):
        setup_apps.check_apps_ready()

def test_get_app_config_returns_correct_app_config(setup_apps):
    """
    Test that get_app_config returns the correct AppConfig instance for a given label.
    """
    app_label = 'myapp'
    mock_app_config = MagicMock()
    mock_app_config.label = app_label
    setup_apps.app_configs[app_label] = mock_app_config

    assert setup_apps.get_app_config(app_label) == mock_app_config

def test_get_app_config_raises_lookup_error_for_invalid_label(setup_apps):
    """
    Test that get_app_config raises LookupError for an invalid app label.
    """
    with pytest.raises(LookupError):
        setup_apps.get_app_config('nonexistent')

@patch('django.apps.registry.apps.is_installed', return_value=False)
def test_is_installed_returns_false_for_non_installed_app(mock_is_installed, setup_apps):
    """
    Test that is_installed returns False for a non-installed app.
    """
    assert setup_apps.is_installed('nonexistent_app') == False

@patch('django.apps.registry.apps.is_installed', return_value=True)
def test_is_installed_returns_true_for_installed_app(mock_is_installed, setup_apps):
    """
    Test that is_installed returns True for an installed app.
    """
    assert setup_apps.is_installed('existent_app') == True

def test_set_available_apps_updates_app_configs(setup_apps):
    """
    Test that set_available_apps updates app_configs correctly.
    """
    mock_app_config = MagicMock()
    mock_app_config.name = 'myapp'
    setup_apps.app_configs['myapp'] = mock_app_config

    setup_apps.set_available_apps(['myapp'])
    assert 'myapp' in setup_apps.app_configs

def test_unset_available_apps_restores_app_configs(setup_apps):
    """
    Test that unset_available_apps restores app_configs to its previous state.
    """
    original_app_configs = setup_apps.app_configs.copy()
    setup_apps.set_available_apps(['myapp'])
    setup_apps.unset_available_apps()
    assert setup_apps.app_configs == original_app_configs

def test_set_installed_apps_resets_and_populates(setup_apps):
    """
    Test that set_installed_apps resets and populates apps.
    """
    with patch.object(setup_apps, 'populate') as mock_populate:
        setup_apps.set_installed_apps(['app1'])
        mock_populate.assert_called_once_with(['app1'])

def test_unset_installed_apps_restores_state(setup_apps):
    """
    Test unset_installed_apps restores the state before set_installed_apps was called.
    """
    original_state = (setup_apps.apps_ready, setup_apps.models_ready, setup_apps.ready)
    setup_apps.set_installed_apps(['app1'])
    setup_apps.unset_installed_apps()
    assert (setup_apps.apps_ready, setup_apps.models_ready, setup_apps.ready) == original_state