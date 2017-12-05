from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from services.acservice.constants import *
from ac_mediator.exceptions import *
from services.mgmt import get_service_by_name
import configparser
import os
import logging
import json

logger = logging.getLogger('management')


def _test_search_component(service, test_config, context):
    query = test_config.get('text_search_query', 'dogs')
    service.clear_response_warnings()
    response = service.text_search(
        context=context, q=query, f=None, s=None, common_search_params={
            'fields': MINIMUM_RESOURCE_DESCRIPTION_FIELDS,
            'size': 10,
            'page': 1,
        })
    warnings = service.collect_response_warnings()
    return {
        'status': 'OK' if len(warnings) == 0 else 'WR',
        'warnings': warnings,
        'response': response
    }


def _test_licensing_component(service, test_config, context):
    resource_id = test_config.get('ac_resource_id_for_licensing')
    service.clear_response_warnings()
    response = service.license(context=context, acid=resource_id)
    warnings = service.collect_response_warnings()
    return {
        'status': 'OK' if len(warnings) == 0 else 'WR',
        'warnings': warnings,
        'response': response
    }


def _test_download_component(service, test_config, context):
    resource_id = test_config.get('ac_resource_id_for_download')
    service.clear_response_warnings()
    response = service.download(context=context, acid=resource_id)
    warnings = service.collect_response_warnings()
    return {
        'status': 'OK' if len(warnings) == 0 else 'WR',
        'warnings': warnings,
        'response': response
    }


def _test_component(service, test_config, component, context):
    """
    This function should test an individual component of a service (e.g. search) and
    return results in json format.
    """
    try:
        if component == SEARCH_TEXT_COMPONENT:
            return _test_search_component(service, test_config, context)
        if component == LICENSING_COMPONENT:
            return _test_licensing_component(service, test_config, context)
        if component == DOWNLOAD_COMPONENT:
            return _test_download_component(service, test_config, context)
    except (ACException, ACAPIException) as e:
        return {
            'status': 'FA',
            'response': '{0}: {1}'.format(e.__class__.__name__, e.msg)
        }
    except NotImplementedError as e:
        return {
            'status': 'FA',
            'response': '{0}: {1}'.format(e.__class__.__name__, e)
        }
    except Exception as e:
        return {
            'status': 'FA',
            'response': 'Unhandled exception: {0}, {1}'.format(e.__class__.__name__, e)
        }
    return {
        'status': 'IN',
        'response': 'Invalid or not supported component'
    }


class Command(BaseCommand):
    help = 'Test an implementation of a 3rd party service integration with the Audio Commons Mediator.'

    def add_arguments(self, parser):
        parser.add_argument('service_name', type=str, help='Name or id of the service to test')
        parser.add_argument('--out_filename', dest='out_filename', type=str,
                            help='Filename where to save the output of the test. '
                                 'Defaults to "out_test_<SERVICE_NAME>.html"')
        parser.add_argument('--test_config_filename', dest='test_config_filename', type=str,
                            help='Filename where to configuration parameters for testing the service are stored.'
                                 'Defaults to "test_services.cfg"')

    def handle(self, *args, **options):
        """
        Iterate over all implemented components by the given service and test them. Output an HTML report
        with the results. Loads configuration parameters for the tests (e.g. query terms) from a file called
        `test_services.cfg` that should be placed in the same directory.
        """

        service_name = options['service_name']
        service = get_service_by_name(service_name)
        logger.info('Testing service {0} with id {1}'.format(service.name, service.id))

        test_config = configparser.ConfigParser()
        test_config_filename = options.get('test_config_filename')
        if test_config_filename is None:
            test_config_filename = 'test_services.cfg'
        test_config_path = os.path.join(test_config_filename)
        test_config.read(test_config_path)
        try:
            test_config = test_config[service.name]
        except KeyError:
            logger.info('No test configuration data found for service {0} in file {1}. '
                        'Aborting...'.format(service.name, test_config_path))
            return

        context = {  # Should return equivalent to api.views.get_request_context
            'user_account_id': 0,  # First version, no accounts supported
            'dev_account_id': 0
        }

        components_results = list()
        for count, component in enumerate(service.components):
            logger.info('\t- testing {0} [{1}/{2}]'.format(component, count + 1, len(service.components)))
            result = _test_component(service, test_config, component, context)
            if isinstance(result['response'], dict):
                result['formatted_response'] = json.dumps(result['response'], indent=4)
                if 'warnings' in result:
                    result['formatted_warnings'] = json.dumps(result['warnings'], indent=4)
            else:
                result['formatted_response'] = result['response']
            components_results.append((component, result))

        html_contents = render_to_string('services/test_service.html', {'service': service,
                                                                        'components_results': components_results})

        out_filename = options.get('out_filename')
        if out_filename is None:
            out_filename = 'out_test_{0}.html'.format(service.name)
        out_path = os.path.join(out_filename)
        with open(out_path, 'w') as fid:
            fid.write(html_contents)

        logger.info('Done! Written test results at {0}'.format(out_path))
