import inspect
import pkgutil
import configparser
from services.classes import BaseACService
from ac_mediator.exceptions import ImproperlyConfiguredACService, ACException, ACServiceDoesNotExist


def _load_services():
    """
    We walk through the modules in services ac-mediator package and instantiate objects
    for those classes which are subclass of BaseACService.
    :return: list of BaseACService instances
    """
    loaded_services = []
    for importer, modname, ispkg in pkgutil.walk_packages(__path__, "services."):
        if not ispkg:
            module = __import__(modname, fromlist="dummy")
            for name, ftype in inspect.getmembers(module, inspect.isclass):
                if issubclass(ftype, BaseACService) and name != 'BaseACService':
                    loaded_services.append(ftype())
    return loaded_services


def _configure_services(loaded_services):
    """
    Configure loaded services and return a list of those that were successfully configured.
    :param loaded_services: list of BaseACService instances
    :return: list of successfully configures BaseACService instances
    """
    config = configparser.ConfigParser()
    config.read('services/services_conf.cfg')
    configured_services = []
    for service in loaded_services:
        try:
            try:
                configuration = config[service.name]
            except KeyError:
                raise ImproperlyConfiguredACService('No configuration section found')
            service.configure(configuration)
            if service.id in [srv.id for srv in configured_services]:
                raise ACException('Each service should have a unique id')
            configured_services.append(service)
        except ImproperlyConfiguredACService as e:
            print('Service {0} could not be configured: {1}'.format(service.name, e))
            continue
    return configured_services


def _load_and_configure_services():
    loaded_services = _load_services()
    return _configure_services(loaded_services)


available_services = _load_and_configure_services()


def get_available_services():
    return available_services


def get_service_by_id(service_id):
    for service in available_services:
        if service.id == service_id:
            return service
    raise ACServiceDoesNotExist
