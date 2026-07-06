from jinja2 import Environment, FileSystemLoader
import os
from app.generator.generators.base import BaseGenerator
from app.generator.graph.builder import GraphBuilder

class DrawioGenerator(BaseGenerator):
    def generate(self, builder: GraphBuilder, **kwargs) -> str:
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template('drawio.xml.j2')
        return template.render(builder=builder, graph=builder.graph)
