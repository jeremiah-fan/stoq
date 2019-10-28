#!/usr/bin/env python3

#   Copyright 2014-2018 PUNCH Cyber Analytics Group
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    .. _stoqoverview:

    Overview
    ========

    `stoQ` is an extremely flexible framework. In this section we will go over some of
    the most advanced uses and show examples of how it can be used as a framework.

    .. _framework:

    Framework
    =========

    stoQ is much more than simply a command to be run. First and foremost, stoQ is a
    framework. The command `stoq` is simply a means of interacting with the framework.
    For more detailed and robust information on APIs available for stoQ, please check
    out the :ref:`plugin documentation <pluginoverview>`.

    ``Stoq`` is the primary class for interacting with `stoQ` and its plugins.
    All arguments, except for plugins to be used, must be defined upon instantiation.
    Plugins can be loaded at any time. However, to ensure consistent
    behavior, it is recommended that all required plugins be loaded
    upon instantiation.

    For these examples, it is assumed the below :ref:`plugins have been installed <installplugins>` in
    `$CWD/plugins`:
        - dirmon
        - exif
        - filedir
        - hash
        - yara


    .. _individualscan:

    Individual Scan
    ---------------

    Individual scans are useful for scanning single payloads at a time. The user is
    responsible for ensuring a payload is passed to the ``Stoq`` class.

    .. note:: ``Provider`` plugins are ignored when conducting an individual scan.

    1. First, import the required class:

        >>> from stoq import Stoq, RequestMeta


    2. We will now define the plugins we want to use. In this case, we will be
       loading the ``hash``, and ``exif`` plugins:

        >>> workers = ['hash', 'exif']


    3. Now that we have our environment defined, lets instantiate the ``Stoq`` class:

        >>> s = Stoq(always_dispatch=workers)


    4. We can now load a payload, and scan it individually with `stoQ`:

        >>> src = '/tmp/bad.exe'
        >>> with open(src, 'rb') as src_payload:
        ...     meta = RequestMeta(extra_data={'filename': src})
        ...     results = await s.scan(
        ...             content=src_payload.read(),
        ...             request_meta=meta)
        >>> print(results)
        ...    {
        ...        "time": "...",
        ...        "results": [
        ...            {
        ...                "payload_id": "...",
        ...                "size": 507904,
        ...                "payload_meta": {
        ...                    "should_archive": true,
        ...                    "extra_data": {
        ...                        "filename": "/tmp/bad.exe"
        ...                    },
        ...                    "dispatch_to": []
        ...                },
        ...                "workers": [
        ...                    {
        ...                        "hash": {
        ... [...]


    .. _providerscan:

    Using Providers
    ---------------

    Using stoQ with providers allows for the scanning of multiple payloads from
    multiple sources. This method will instantiate a `Queue` which payloads
    are published to for scanning by `stoQ`. Additionally, payloads may be
    retrieved from multiple disparate data sources using `Archiver` plugins.

    1. First, import the required class:

        >>> from stoq import Stoq


    2. We will now define the plugins we want to use. In this case, we will be
       loading the ``dirmon``, ``filedir``, ``hash``, and ``exif`` plugins. We
       will also set the ``base_dir`` to a specific directory. Additionally,
       we will also set some plugin options to ensure the plugins are
       operating the way we'd like them:

        >>> always_dispatch = ['hash']
        >>> providers = ['dirmon']
        >>> connectors = ['filedir']
        >>> dispatchers = ['yara']
        >>> plugin_opts = {
        ...     'dirmon': {'source_dir': '/tmp/datadump'},
        ...     'filedir': {'results_dir': '/tmp/stoq-results'}
        ... }
        >>> base_dir = '/usr/local/stoq'
        >>> plugin_dirs = ['/opt/plugins']


    .. note:: Any plugin options available in the plugin's ``.stoq`` configuration
              file can be set via the ``plugin_opts`` argument.

    3. Now that we have our environment defined, lets instantiate the ``Stoq`` class,
    and run:

        >>> s = Stoq(
        ...     base_dir=base_dir,
        ...     plugin_dir_list=plugin_dirs,
        ...     dispatchers=dispatchers,
        ...     providers=providers,
        ...     connectors=connectors,
        ...     plugins_opts=plugins_opts,
        ...     always_dispatch=always_dispatch
        ... )
        >>> await s.run()


    A few things are happening here:
        #. The ``/tmp/datadump`` directory is being monitored for newly created files
        #. Each file is opened, and the payload is loaded into ``Stoq`` asynchronously
        #. The payload is scanned with the ``yara`` dispatcher plugin
        #. The yara dispatcher plugin returns a list of plugins that the payload should
           be scanned with
        #. The plugins identified by the ``yara`` dispatcher are loaded, and the payload is
           sent to them
        #. Each payload will always be sent to the ``hash`` plugin because it was defined
           in ``always_dispatch``
        #. The results from all plugins are collected, and sent to the ``filedir``
           connector plugin
        #. The ``filedir`` plugin saves each result to disk in ``/tmp/stoq-results``

    .. _manualscan:

    Manual Interaction
    ==================

    ``Stoq`` may also be interacted with manually, rather than relying on the normal workflow.
    In this section, we will touch on how this can be done.

    Instantiating stoQ
    ------------------

    Let's start by simply instantiating ``Stoq`` with no options. There are several arguments
    available when instantiating ``Stoq``, please refer to the :ref:`plugin documentation <pluginoverview>`
    for more information and options available.:

        >>> from stoq import Stoq
        >>> s = Stoq()


    Loading plugins
    ---------------

    `stoQ` plugins can be loaded using a simple helper function. The framework will
    automatically detect the type of plugin is it based on the ``class`` of the plugin.
    There is no need to define the plugin type, `stoQ` will handle that once it is loaded.:

        >>> plugin = s.load_plugin('yara')


    Instantiate Payload Object
    --------------------------

    In order to scan a payload, a ``Payload`` object must first be instantiated. The
    ``Payload`` object houses all information related to a payload, to include the
    content of the payload and metadata (i.e., size, originating plugin information,
    dispatch metadata, among others) pertaining to the payload. Optionally, a ``Payload``
    object can be instantiated with a ``PayloadMeta`` object to ensure the originating
    metadata (i.e., filename, source path, etc...) is also made available:

        >>> import os
        >>> from stoq.data_classes import PayloadMeta, Payload
        >>> filename = '/tmp/test_file.exe'
        >>> with open(filename, 'rb') as src:
        ...    meta = PayloadMeta(
        ...        extra_data={
        ...            'filename': os.path.basename(filename),
        ...            'source_dir': os.path.dirname(filename),
        ...        }
        ...    )
        >>> payload = Payload(src.read(), meta)


    Scan payload
    ------------
    There are two helper functions available for scanning a payload. If a dispatcher
    plugin is not being used, then a worker plugin must be defined by passing the
    ``add_start_dispatch`` argument. This tells `stoQ` to send the ``Payload`` object
    to the specified worker plugins.

    From raw bytes
    ^^^^^^^^^^^^^^

    If a `Payload` object has not been created yet, the content of the raw payload can
    simply be passed to the `Stoq.scan` function. A ``Payload`` object will automatically
    be created.:

        >>> start_dispatch = ['yara']
        >>> results = await s.scan('raw bytes', add_start_dispatch=start_dispatch)


    From ``Payload`` object
    ^^^^^^^^^^^^^^^^^^^^^^^

    If a ``Payload`` object has already been instatiated, as detailed above, the
    ``scan_request`` function may be called:

        >>> start_dispatch = ['yara']
        >>> results = await s.scan_request(payload, add_start_dispatch=start_dispatch)


    Save Results
    ------------

    Finally, results may be saved using the desired ``Connector`` plugin. `stoQ` stores
    results from the framework as a ``StoqResponse`` object. The results will be saved
    to all connector plugins that have been loaded. In this example, we will only load
    the ``filedir`` plugin which will save the results to a specified directory.:

        >>> connector = s.load_plugin('filedir')
        >>> await connector.save(results)

    Split Results
    -------------

    In some cases it may be required to split results out individually. For example, when
    saving results to different indexes depending on plugin name, such as with ElasticSearch or Splunk.

        >>> results = await s.scan_request(payload)
        >>> results.split()

    Reconstructing Subresponse Results
    ----------------------------------

    stoQ can produce complex results depending on the recursion depth and extracted payload objects.
    In order to help handle complex results and limit redundant processing of payloads when using
    stoQ as a framework, a method exists that will allow for iterating over each result as if it
    were the original root object. This is especially useful when handling compressed archives, such
    as `zip` or `apk` files that may have multiple levels of archived content. Additionally, the
    defined decorators will be run against each newly constructed `StoqResponse` and added to the
    results.

        >>> await for result in s.reconstruct_all_subresponses(results):
        ...     print(result)

    Below is a simple flow diagram of the iterated results when being reconstructed.

    .. image:: /_static/reconstruct-results.png


    .. _multiplugindir:

    Multiple Plugin directories
    ===========================

    When instantiating ``Stoq``, multiple plugins directories may be defined. For more
    information on default paths, please refer to the :ref:`getting started documentation <stoqhome>`::

        >>> from stoq import Stoq
        >>> plugins_directories = ['/usr/local/stoq/plugins', '/home/.stoq/plugins']
        >>> s = Stoq(plugin_dir_list=plugins_directories)


    API
    ===

"""

import asyncio
import configparser
import logging
import os
from collections import defaultdict
from logging.handlers import RotatingFileHandler
from typing import (
    AsyncGenerator,
    Awaitable,
    Coroutine,
    DefaultDict,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import stoq.helpers as helpers
from pythonjsonlogger import jsonlogger  # type: ignore
from stoq.data_classes import (
    ArchiverResponse,
    DecoratorResponse,
    DispatcherResponse,
    Error,
    Payload,
    PayloadMeta,
    PayloadResults,
    Request,
    RequestMeta,
    StoqResponse,
    WorkerResponse,
)
from stoq.plugin_manager import StoqPluginManager
from stoq.plugins import (
    ArchiverPlugin,
    ConnectorPlugin,
    DecoratorPlugin,
    DispatcherPlugin,
    WorkerPlugin,
)
from stoq.utils import ratelimited

from .exceptions import StoqException


# Created to enable `None' as a valid paramater
_UNSET = object()


class Stoq(StoqPluginManager):
    def __init__(
        self,
        base_dir: Optional[str] = None,
        config_file: Optional[str] = None,
        log_dir: Optional[Union[str, object]] = _UNSET,
        log_level: Optional[str] = None,
        plugin_dir_list: Optional[List[str]] = None,
        plugin_opts: Optional[Dict[str, Dict]] = None,
        providers: Optional[List[str]] = None,
        source_archivers: Optional[List[str]] = None,
        dest_archivers: Optional[List[str]] = None,
        connectors: Optional[List[str]] = None,
        dispatchers: Optional[List[str]] = None,
        decorators: Optional[List[str]] = None,
        always_dispatch: Optional[List[str]] = None,
        max_recursion: Optional[int] = None,
        max_required_worker_depth: Optional[int] = None,
    ) -> None:
        """

        Core Stoq Class

        :param base_dir: Base directory for stoQ
        :param config_file: stoQ Configuration file
        :param log_dir: Path to log directory
        :param log_level: Log level for logging events
        :param plugin_dir_list: Paths to search for stoQ plugins
        :param plugin_opts: Plugin specific options that are passed once a plugin is loaded
        :param providers: Provider plugins to be loaded and run for sending payloads to scan
        :param source_archivers: Archiver plugins to be used for loading payloads for analysis
        :param dest_archiver: Archiver plugins to be used for archiving payloads and extracted payloads
        :param connectors: Connectors to be loaded and run for saving results
        :param dispatchers: Dispatcher plugins to be used
        :param decorators: Decorators to be used
        :param always_dispatch: Plugins to always send payloads to, no matter what
        :param max_recursion: Maximum level of recursion into a payload and extracted payloads
        :param max_required_worker_depth: Maximum depth for required worker plugins dependencies
    ) -> None:
        """
        if not base_dir:
            base_dir = os.getcwd()
        base_dir = os.path.realpath(base_dir)
        config_file = config_file if config_file else os.path.join(base_dir, 'stoq.cfg')

        config = configparser.ConfigParser(allow_no_value=True)
        if os.path.exists(config_file):
            config.read(config_file)

        self.max_queue = config.getint('core', 'max_queue', fallback=100)
        self.provider_consumers = config.getint(
            'core', 'provider_consumers', fallback=50
        )
        self.max_recursion = max_recursion or config.getint(
            'core', 'max_recursion', fallback=3
        )
        self.max_required_worker_depth = max_required_worker_depth or config.getint(
            'core', 'max_required_worker_depth', fallback=3
        )

        if log_dir is _UNSET:
            log_dir = config.get(
                'core', 'log_dir', fallback=os.path.join(base_dir, 'logs')
            )
        if not log_level:
            log_level = config.get('core', 'log_level', fallback='INFO')
        log_maxbytes = int(config.get('core', 'log_maxbytes', fallback='1500000'))
        log_backup_count = int(config.get('core', 'log_backup_count', fallback='5'))
        log_syntax = config.get('core', 'log_syntax', fallback='text')
        self._init_logger(
            log_dir,  # type: ignore
            log_level,  # type: ignore
            log_maxbytes,
            log_backup_count,
            log_syntax,
        )

        if not plugin_dir_list:
            plugin_dir_str = config.get(
                'core', 'plugin_dir_list', fallback=os.path.join(base_dir, 'plugins')
            )
            plugin_dir_list = [d.strip() for d in plugin_dir_str.split(',')]

        super().__init__(plugin_dir_list, plugin_opts, config)

        if not providers:
            providers_str = config.get('core', 'providers', fallback='')
            providers = [d.strip() for d in providers_str.split(',') if d.strip()]
        self._loaded_provider_plugins = {  # type: ignore
            d: self.load_plugin(d) for d in providers if d  # type: ignore
        }
        if not source_archivers:
            source_arch_str = config.get('core', 'source_archivers', fallback='')
            source_archivers = [
                d.strip() for d in source_arch_str.split(',') if d.strip()
            ]
        self._loaded_source_archiver_plugins = {  # type: ignore
            d: self.load_plugin(d) for d in source_archivers if d  # type: ignore
        }
        if not dest_archivers:
            dest_arch_str = config.get('core', 'dest_archivers', fallback='')
            dest_archivers = [d.strip() for d in dest_arch_str.split(',') if d.strip()]
        self._loaded_dest_archiver_plugins = {  # type: ignore
            d: self.load_plugin(d) for d in dest_archivers if d  # type: ignore
        }
        if not connectors:
            conn_str = config.get('core', 'connectors', fallback='')
            connectors = [d.strip() for d in conn_str.split(',') if d.strip()]
        self._loaded_connector_plugins = [
            self.load_plugin(d) for d in connectors if d  # type: ignore
        ]
        if not dispatchers:
            dispatcher_str = config.get('core', 'dispatchers', fallback='')
            dispatchers = [d.strip() for d in dispatcher_str.split(',') if d.strip()]
        self._loaded_dispatcher_plugins = {  # type: ignore
            d: self.load_plugin(d) for d in dispatchers if d  # type: ignore
        }
        if not decorators:
            decorator_str = config.get('core', 'decorators', fallback='')
            decorators = [d.strip() for d in decorator_str.split(',') if d.strip()]
        self._loaded_decorator_plugins = {  # type: ignore
            d: self.load_plugin(d) for d in decorators if d  # type: ignore
        }
        self.always_dispatch = always_dispatch
        if not self.always_dispatch:
            ad_str = config.get('core', 'always_dispatch', fallback='')
            self.always_dispatch = [d.strip() for d in ad_str.split(',') if d.strip()]
            for ad in self.always_dispatch:
                self.load_plugin(ad)

    #  @ratelimited()
    async def scan(
        self,
        content: bytes,
        payload_meta: Optional[PayloadMeta] = None,
        request_meta: Optional[RequestMeta] = None,
        add_start_dispatch: Optional[List[str]] = None,
        ratelimit: Optional[str] = None,
    ) -> StoqResponse:
        """

        Wrapper for `scan_request` that creates a `Payload` object from bytes

        :param content: Raw bytes to be scanned
        :param payload_meta: Metadata pertaining to originating source
        :param request_meta: Metadata pertaining to the originating request
        :param add_start_dispatch: Force first round of scanning to use specified plugins
        :param ratelimit: Rate limit calls to scan

        :return: Complete scan results
        :rtype: StoqResponse

        """
        self.log.debug(
            f'Content received ({len(content)} bytes): '
            f'PayloadMeta: {helpers.dumps(payload_meta, indent=0)}, '
            f'RequestMeta: {helpers.dumps(request_meta, indent=0)}'
        )
        payload_meta = payload_meta or PayloadMeta()
        payload = Payload(content, payload_meta)
        request_meta = request_meta or RequestMeta()
        request = Request(payloads=[payload], request_meta=request_meta)
        return await self.scan_request(request, add_start_dispatch)

    async def scan_request(
        self, request: Request, add_start_dispatch: Optional[List[str]] = None
    ) -> StoqResponse:
        """

        Scan an individual payload

        :param request: ``Request`` object of payload(s) to be scanned
        :param add_start_dispatch: Force first round of scanning to use specified plugins

        :return: Complete scan results
        :rtype: StoqResponse

        """

        self.log.debug(
            f'Request received: RequestMeta: {helpers.dumps(request.request_meta, indent=0)}, '
            f'start_dispatches: {helpers.dumps(add_start_dispatch, indent=0)}'
        )

        add_start_dispatch: List[str] = add_start_dispatch or []
        scan_queue: List[Tuple[Payload, List[str]]] = []
        deferred: Set[Tuple[Payload, WorkerPlugin]] = set()

        hashes_seen: DefaultDict[str, List] = defaultdict(list)
        for idx, payload in enumerate(request.payloads):
            if payload.results.payload_meta.should_scan:
                scan_queue.append((payload, add_start_dispatch))

            sha = helpers.get_sha256(payload.content)
            hashes_seen[sha].append(idx)

        for _recursion_level in range(self.max_recursion + 1):
            if len(scan_queue) <= 0 and len(deferred) <= 0:
                break

            # Commence worker round
            self.log.debug(f'Current payload recursion depth: {_recursion_level}')
            next_scan_queue: List[Tuple[Payload, List[str]]] = []
            next_deferred: Set[Tuple[Payload, WorkerPlugin]] = set()

            nested_worker_tasks: List[
                Set[Tuple[Payload, WorkerPlugin]]
            ] = await asyncio.gather(
                *[
                    self._generate_tasks(payload, add_dispatch, request)
                    for payload, add_dispatch in scan_queue
                    if payload.results.payload_meta.should_scan
                ]
            )
            nested_worker_tasks.append(deferred)

            tasks = []
            for worker_tasks in nested_worker_tasks:
                for payload, plugin in worker_tasks:
                    if plugin.plugin_name in payload.results.plugins_run['workers']:
                        continue

                    if self._worker_task_can_start(payload, plugin):
                        tasks.append(self._single_scan(payload, plugin, request))
                    else:
                        next_deferred.add((payload, plugin))

            self.log.debug(f'Tasks in round {_recursion_level + 1}: {tasks}')
            self.log.debug(f'Deferred to future executions: {next_deferred}')

            # TODO: Add option for no-dedup
            nested_extracted_results = await asyncio.gather(*tasks)
            for extracted_results in nested_extracted_results:
                for extracted_result in extracted_results:
                    ex_hash = helpers.get_sha256(extracted_result.content)
                    if ex_hash not in hashes_seen:
                        self.log.debug(
                            f'Adding extracted payload to scan queue: {ex_hash}, '
                            f'PayloadMeta: {extracted_result.results.payload_meta}'
                        )
                        request.payloads.append(extracted_result)
                        hashes_seen[ex_hash].append(len(request.payloads) - 1)
                        if _recursion_level >= self.max_recursion:
                            request.errors.append(
                                Error(
                                    error=f'Max recursion level ({self.max_recursion}) reached, unable to process payload',
                                    payload_id=extracted_result.results.payload_id,
                                )
                            )
                        next_scan_queue.append(
                            (
                                extracted_result,
                                extracted_result.results.payload_meta.dispatch_to,
                            )
                        )
                    else:
                        payload_idx = hashes_seen[ex_hash]
                        for idx in payload_idx:
                            request.payloads[idx].results.extracted_by.extend(
                                extracted_result.results.extracted_by
                            )
                            request.payloads[idx].results.extracted_from.extend(
                                extracted_result.results.extracted_from
                            )

            scan_queue = next_scan_queue
            deferred = next_deferred

        archive_tasks: List = []
        for payload in request.payloads:
            if (
                request.request_meta.archive_payloads
                and payload.results.payload_meta.should_archive
            ):
                for archiver_name, archiver in self._loaded_dest_archiver_plugins.items():
                    archive_tasks.append(self._apply_archiver(archiver, payload, request))
        await asyncio.gather(*archive_tasks)

        response = StoqResponse(request=request)

        decorator_tasks = []
        for plugin_name, decorator in self._loaded_decorator_plugins.items():
            decorator_tasks.append(self._apply_decorators(decorator, response))
        await asyncio.gather(*decorator_tasks)

        connector_tasks = []
        for connector in self._loaded_connector_plugins:
            connector_tasks.append(self._save_result(connector, response))
        await asyncio.gather(*connector_tasks)
        return response

    async def run(
        self,
        request_meta: Optional[RequestMeta] = None,
        add_start_dispatch: Optional[List[str]] = None,
    ) -> None:
        """

        Run stoQ using a provider plugin to scan multiple files until exhaustion

        :param request_meta: Metadata pertaining to the originating request
        :param add_start_dispatch: Force first round of scanning to use specified plugins

        """
        # Don't initialize any (provider) plugins here! They should be
        # initialized on stoq start-up or via load_plugin()
        if not self._loaded_provider_plugins:
            raise StoqException('No activated provider plugins')

        self.log.debug(
            f'Starting provider queue: RequestMeta: {request_meta}, '
            f'start_dispatches: {add_start_dispatch}'
        )
        payload_queue: asyncio.Queue = asyncio.Queue(maxsize=self.max_queue)
        providers = [
            asyncio.ensure_future(plugin.ingest(payload_queue))
            for name, plugin in self._loaded_provider_plugins.items()
        ]
        workers = [
            asyncio.ensure_future(
                self._consume(payload_queue, request_meta, add_start_dispatch)
            )
            for n in range(self.provider_consumers)
        ]
        try:
            await asyncio.gather(*providers)
            await payload_queue.join()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.log.exception(e, exc_info=True)
        finally:
            for worker in workers:
                worker.cancel()
                self.log.debug('Cancelling provider worker')

    async def _consume(
        self,
        payload_queue: asyncio.Queue,
        request_meta: Optional[RequestMeta] = None,
        add_start_dispatch: Optional[List[str]] = None,
    ) -> None:
        while True:
            try:
                task = await payload_queue.get()
                # Determine whether the provider has returned a `Payload`, or a task.
                # If it is a task, load the defined archiver plugin to load the
                # `Payload`, otherwise, simply continue on with the scanning.
                if isinstance(task, Payload):
                    request = Request([task], request_meta)
                    await self.scan_request(request, add_start_dispatch)
                else:
                    for source_archiver, task_meta in task.items():
                        self.log.debug(
                            f'Provider task received: source_archiver: {source_archiver}, '
                            f'task_meta: {task_meta}'
                        )
                        try:
                            ar = ArchiverResponse(task_meta)
                            payload = await self._loaded_source_archiver_plugins[
                                source_archiver
                            ].get(ar)
                            if payload:
                                request = Request([payload], request_meta)
                                await self.scan_request(request, add_start_dispatch)
                        except Exception as e:
                            self.log.warn(
                                f'"{task_meta}" failed with archiver "{source_archiver}": {str(e)}'
                            )
                payload_queue.task_done()
            except asyncio.QueueEmpty:
                pass

    async def _single_scan(
        self, payload: Payload, plugin: WorkerPlugin, request: Request
    ) -> List[Payload]:
        self.log.debug(
            f'Scanning Payload {payload.results.payload_id} with WorkerPlugin {plugin.plugin_name}'
        )
        try:
            worker_response: Optional[WorkerResponse] = await plugin.scan(
                payload, request
            )
        except Exception as e:
            worker_response = None
            msg = 'worker:failed to scan'
            self.log.exception(msg)
            request.errors.append(
                Error(
                    payload_id=payload.results.payload_id,
                    plugin_name=plugin.plugin_name,
                    error=helpers.format_exc(e, msg=msg),
                )
            )
        payload.results.plugins_run['workers'].append(plugin.plugin_name)

        if not worker_response:
            return list()

        if worker_response.errors:
            request.errors.extend(worker_response.errors)

        if worker_response.results:
            payload.results.workers[plugin.plugin_name] = worker_response.results

        extracted = [
            Payload(
                content=ex.content,
                payload_meta=ex.payload_meta,
                extracted_by=plugin.plugin_name,
                extracted_from=payload.results.payload_id,
            )
            for ex in worker_response.extracted
        ]
        self.log.debug(
            f'Completed scan of {payload.results.payload_id} with {len(payload.results.workers)} results, '
            f'{len(extracted)} extracted payloads'
        )
        return extracted

    async def _apply_archiver(
        self, archiver: ArchiverPlugin, payload: Payload, request: Request
    ) -> None:
        archiver_response: Union[ArchiverResponse, None] = None
        self.log.debug(
            f'Archiving {payload.results.payload_id} with {archiver.plugin_name}'
        )
        try:
            archiver_response = await archiver.archive(payload, request)
        except Exception as e:
            msg = 'archiver:failed to archive'
            self.log.exception(msg)
            request.errors.append(
                Error(
                    payload_id=payload.results.payload_id,
                    plugin_name=archiver.plugin_name,
                    error=helpers.format_exc(e, msg=msg),
                )
            )

        payload.results.plugins_run['archivers'].append(archiver.plugin_name)
        if archiver_response is not None:
            if archiver_response.errors:
                request.errors.extend(archiver_response.errors)
            if archiver_response.results is not None:
                payload.results.archivers[archiver.plugin_name] = archiver_response.results

    async def _generate_tasks(
        self, payload: Payload, add_dispatch: List[str], request: Request
    ) -> Set[Tuple[Payload, WorkerPlugin]]:
        tot_dispatched_workers: Set[str] = set(add_dispatch).union(self.always_dispatch)
        dispatch_results: List[Set[str]] = await asyncio.gather(
            *[
                self._get_dispatched_plugin_names(dispatcher, payload, request)
                for dispatcher in self._loaded_dispatcher_plugins.values()
            ]
        )
        for dispatched_workers in dispatch_results:
            tot_dispatched_workers.update(dispatched_workers)

        tasks: Set[Tuple[Payload, WorkerPlugin]] = set()
        for dispatched_worker in tot_dispatched_workers:
            # Check cache
            plugins_to_run_cache = request.plugins_to_run_cache.get(dispatched_worker)
            if plugins_to_run_cache:
                # Cache hit
                self.log.debug(f'Cache hit for all plugins to run for {dispatched_worker}: {plugins_to_run_cache}')
                all_generated_plugins: Set[WorkerPlugin] = {
                    self.load_plugin(plugin_name)
                    for plugin_name in plugins_to_run_cache
                }
            else:
                # Cache miss, resolve dependency chain
                all_generated_plugins: Set[WorkerPlugin] = self._generate_plugins(
                    payload, dispatched_worker, request, set()
                )
                request.plugins_to_run_cache[dispatched_worker] = [
                    plugin.plugin_name
                    for plugin in all_generated_plugins
                ]

            if len(all_generated_plugins) == 0: # Error was already recorded
                continue

            tasks.update((payload, plugin) for plugin in all_generated_plugins)

        return tasks

    def _generate_plugins(
        self,
        payload: Payload,
        plugin_name: str,
        request: Request,
        init_plugin_dependency_chain: Set[str],
        depth: int = 0,
    ) -> Set[WorkerPlugin]:
        self.log.debug(f'Checking plugin dependencies for {plugin_name}')
        if plugin_name in init_plugin_dependency_chain:
            msg = f'Circular required plugin dependency found, unable to process plugin {plugin_name}.'
            self.log.error(msg)
            request.errors.append(
                Error(
                    payload_id=payload.results.payload_id,
                    plugin_name=plugin_name,
                    error=msg
                )
            )
            return set()

        if depth > self.max_required_worker_depth:
            request.errors.append(
                Error(
                    payload_id=payload.results.payload_id,
                    plugin_name=plugin_name,
                    error=f'Max required plugin depth ({self.max_required_worker_depth}) reached, unable to generate additional tasks',
                )
            )
            return set()

        self.log.debug(f'Current task recursion depth = {depth}')
        try:
            plugin: WorkerPlugin = self.load_plugin(plugin_name)
        except Exception as e:
            msg = 'worker:failed to load'
            self.log.exception(msg)
            request.errors.append(
                Error(
                    payload_id=payload.results.payload_id,
                    plugin_name=plugin_name,
                    error=helpers.format_exc(e, msg=msg),
                )
            )
            return set()

        all_generated_plugins: Set[WorkerPlugin] = set()
        all_generated_plugins.add(plugin)
        if len(plugin.required_plugin_names) != 0:
            plugin_dependency_chain = init_plugin_dependency_chain.copy()
            plugin_dependency_chain.add(plugin_name)

            self.log.debug(
                f'{plugin_name} has dependencies of {", ".join(plugin.required_plugin_names)}'
            )
            for required_plugin_name in plugin.required_plugin_names:
                generated_plugins = self._generate_plugins(
                    payload,
                    required_plugin_name,
                    request,
                    plugin_dependency_chain,
                    depth + 1,
                )
                if len(generated_plugins) == 0: # Bubble up failure
                    return set()

                all_generated_plugins.update(generated_plugins)
        return all_generated_plugins

    def _worker_task_can_start(self, payload: Payload, worker_plugin: WorkerPlugin):
        for required_plugin_name in worker_plugin.required_plugin_names:
            if required_plugin_name not in payload.results.plugins_run['workers']:
                return False
        return True

    def _init_logger(
        self,
        log_dir: Union[object, str],
        log_level: str,
        log_maxbytes: int,
        log_backup_count: int,
        log_syntax: str,
    ) -> None:
        self.log = logging.getLogger('stoq')
        self.log.setLevel(log_level.upper())

        if log_syntax == 'json':
            formatter = jsonlogger.JsonFormatter  # type: ignore
        else:
            formatter = logging.Formatter

        stderr_handler = logging.StreamHandler()
        stderr_logformat = formatter(
            '[%(asctime)s %(levelname)s] %(name)s: ' '%(message)s'
        )
        stderr_handler.setFormatter(stderr_logformat)
        self.log.addHandler(stderr_handler)

        if log_dir:
            # Let's attempt to make the log directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)  # type: ignore
            log_path = os.path.abspath(
                os.path.join(log_dir, 'stoq.log')  # type: ignore
            )
            file_handler = RotatingFileHandler(
                filename=log_path,
                mode='a',
                maxBytes=log_maxbytes,
                backupCount=log_backup_count,
            )
            file_logformat = formatter(
                '%(asctime)s %(levelname)s %(name)s:'
                '%(filename)s:%(funcName)s:%(lineno)s: '
                '%(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )
            file_handler.setFormatter(file_logformat)
            self.log.addHandler(file_handler)
            self.log.debug(f'Writing logs to {log_path}')

    async def _get_dispatched_plugin_names(
        self, dispatcher: DispatcherPlugin, payload: Payload, request: Request
    ) -> Set[str]:
        self.log.debug(
            f'Sending {payload.results.payload_id} to dispatcher ({dispatcher.plugin_name})'
        )

        plugin_names: Set[str] = set()
        try:
            dispatcher_result = await dispatcher.get_dispatches(payload, request)
        except Exception as e:
            msg = 'dispatcher:failed to dispatch'
            self.log.exception(msg)
            request.errors.append(
                Error(
                    plugin_name=dispatcher.plugin_name,
                    error=helpers.format_exc(e, msg=msg),
                    payload_id=payload.results.payload_id,
                )
            )
            return plugin_names

        if dispatcher_result:
            if dispatcher_result.plugin_names:
                plugin_names.update(dispatcher_result.plugin_names)

            if dispatcher_result.meta:
                payload.dispatch_meta[dispatcher.plugin_name] = dispatcher_result.meta

            self.log.debug(
                f'Dispatching {payload.results.payload_id} to {dispatcher_result.plugin_names}'
            )
        return plugin_names

    async def _apply_decorators(
        self, decorator: DecoratorPlugin, response: StoqResponse
    ) -> StoqResponse:
        """Mutates the given StoqResponse object to include decorator information"""
        self.log.debug(f'Applying decorator {decorator.plugin_name}')
        try:
            decorator_response = await decorator.decorate(response)
        except Exception as e:
            msg = 'decorator'
            self.log.exception(msg)
            error = Error(
                plugin_name=decorator.plugin_name, error=helpers.format_exc(e, msg=msg)
            )
            response.errors.append(error)
            return response
        if decorator_response is None:
            return response
        if decorator_response.results is not None:
            response.decorators[decorator.plugin_name] = decorator_response.results
        if decorator_response.errors:
            response.errors.extend(decorator_response.errors)
        return response

    async def _save_result(
        self, connector: ConnectorPlugin, response: StoqResponse
    ) -> None:
        self.log.debug(f'Saving results to connector {connector.plugin_name}')
        try:
            await connector.save(response)
        except Exception:
            self.log.exception(
                f'Failed to save results using {connector.__module__}: {response}'
            )

    async def reconstruct_all_subresponses(
        self, stoq_response: StoqResponse
    ) -> AsyncGenerator[StoqResponse, None]:
        for i, new_root_payload_result in enumerate(stoq_response.results):
            parent_payload_ids = {stoq_response.results[i].payload_id}
            # Contruct a new root Payload object since StoqResponse only has the
            # PayloadResults object
            new_root_payload = Payload(b'')
            new_root_payload.results = new_root_payload_result
            relevant_payloads: List[Payload] = [new_root_payload]

            for payload_result in stoq_response.results[i:]:
                for extracted_from in payload_result.extracted_from:
                    if extracted_from in parent_payload_ids:
                        parent_payload_ids.add(payload_result.payload_id)
                        new_payload = Payload(b'')
                        new_payload.results = payload_result
                        relevant_payloads.append(new_payload)

            new_request = Request(
                payloads=relevant_payloads, request_meta=stoq_response.request_meta
            )
            new_response = StoqResponse(
                request=new_request,
                time=stoq_response.time,
                scan_id=stoq_response.scan_id,
            )
            decorator_tasks = []
            for plugin_name, decorator in self._loaded_decorator_plugins.items():
                decorator_tasks.append(self._apply_decorators(decorator, new_response))
            await asyncio.gather(*decorator_tasks)
            yield new_response
