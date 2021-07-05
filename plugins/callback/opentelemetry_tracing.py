from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from ansible.plugins.callback import CallbackBase

from datetime import datetime
from os import getenv

class CallbackModule(CallbackBase):
    """
    This callback module generates OpenTelemetry (Jaeger) traces.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'sebthebert.opentelemetry.tracing'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        super(CallbackModule, self).__init__()
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer("ansible")
        jaeger_host = getenv('ANSIBLE_OT_JAEGER_HOST', '127.0.0.1')
        jaeger_port = getenv('ANSIBLE_OT_JAEGER_PORT', 6831)
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
            )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        tracer = trace.get_tracer(__name__)
        self.tracer = tracer
        self.span_playbook = None
        self.span_play = None
        self.span_task = {}
        self.current_play = ''
        self._display.display(msg=f"{datetime.now()} | opentelemetry.tracing plugin configured to export traces to '{jaeger_host}:{jaeger_port}'")

    def v2_playbook_on_start(self, playbook):
        self._display.display(msg=f"{datetime.now()} | v2_playbook_on_start({playbook._file_name})")
        span_playbook = self.tracer.start_span(f"Playbook '{playbook._file_name}'")
        self.span_playbook = span_playbook
    
    def v2_playbook_on_play_start(self, play):
        self._display.display(msg=f"{datetime.now()} | v2_playbook_on_play_start({play.name})")
        if play.name != self.current_play and self.span_play:
            self.span_play.end()
        if play.name != self.current_play:
            context = trace.set_span_in_context(self.span_playbook)
            span_play = self.tracer.start_span(f"Play '{play.name}'", context=context)
            self.span_play = span_play
            self.current_play = play.name

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._display.debug(msg=f"{datetime.now()} | v2_playbook_on_task_start({task.name}, {is_conditional})")

    def v2_runner_on_start(self, host, task):
        self._display.debug(msg=f"{datetime.now()} | v2_runner_on_start({host.name}, {task.name}) {task}")
        context = trace.set_span_in_context(self.span_play)
        span_task = self.tracer.start_span(f"Task '{task.name}' on '{host.name}'", context=context)
        self.span_task[host.name] = span_task

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        self._display.debug(msg=f"{datetime.now()} | v2_runner_on_failed({host})")
        self.span_task[host].end()

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        self._display.debug(msg=f"{datetime.now()} | v2_runner_on_ok({host})")
        self.span_task[host].end()

    def v2_playbook_on_stats(self, stats):
        self._display.debug(msg=f"{datetime.now()} | v2_playbook_on_stats()")
        self.span_play.end()
        self.span_playbook.end()
