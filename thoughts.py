import web
import markdown

import os

base_path = "./"
thoughts_path = base_path + "thoughts/"
templates_path = base_path + "templates/"

urls = (
    '/', 'Home',
    '/(.*)', 'Thoughts',
)

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

render = web.template.render(templates_path)
renderpage = web.template.render(templates_path)

def has_suffix(str, suffix):
    return str[-len(suffix):] == suffix

def thoughts_all():
    for filename in os.listdir(thoughts_path):
        if    has_suffix(filename, ".md") \
           or has_suffix(filename, ".markdown"):
            yield filename

def thought_get(name):
    filenames = [thoughts_path + name,
                 thoughts_path + name + ".md",
                 thoughts_path + name + ".markdown"]

    for filename in filenames:
        try:
            with open(filename) as file:
                return file.read()

        except IOError:
            pass

    return None

class Home:
    def GET(self):
        return renderpage.home([render.inlinethought(thoughtname, thought_get(thoughtname))
                                for thoughtname in thoughts_all()])

class Thoughts:
    def GET(self, name):
        thought = thought_get(name)

        if thought is None:
            raise web.notfound()

        return markdown.markdown(thought)

if __name__ == "__main__":
    app.run()
