import web
import markdown
import simplejson

import os

base_path = "./"
thoughts_path = base_path + "thoughts/"
templates_path = base_path + "templates/"

urls = (
    '/', 'HomeServer',
	'/tag/(.*)', 'TagServer',
    '/(.*)', 'ThoughtServer',
)

def notfound():
    return renderpage.notfound()

app = web.application(urls, globals(), autoreload=False)
app.notfound = notfound

application = app.wsgifunc()

render = web.template.render(templates_path)
renderpage = web.template.render(templates_path, base="index")

def has_suffix(str, suffix):
    return str[-len(suffix):] == suffix

def thoughts_all():
    for filename in os.listdir(thoughts_path):
        if    has_suffix(filename, ".md") \
           or has_suffix(filename, ".markdown"):
            yield thought_get(filename)

def thoughts_by_tag(tag):
	return filter(lambda thought: tag in thought.tags, thoughts_all())
			
def thought_get(name):
    filenames = [thoughts_path + name,
                 thoughts_path + name + ".md",
                 thoughts_path + name + ".markdown"]

    for filename in filenames:
        try:
            with open(filename) as file:
                return Thought(name, file.read())

        except IOError:
            pass

    return None

class Thought:
	def __init__(self, name, str):
		self.title = ""
		self.tags = []
		self.contents = str
		#Remove extension
		self.name = name[:name.rfind(".")]
		
		str_split = str.split("\n", 1)
		
		#Doesn't have a metadata / empty file
		if str[0] != "{" or len(str_split) == 1:
			pass
		
		else:
			try:
				metadata = simplejson.loads(str_split[0])
				self.contents = str_split[1]
				
				#Import the relevant keys from the metadata into self
				for key in ["title", "tags"]:
					if key in metadata:
						setattr(self, key, metadata[key])
						
			except simplejson.decoder.JSONDecodeError:
				pass
					
		self.marked_contents = markdown.markdown(self.contents)
	
class HomeServer:
    def GET(self):
        thoughts = [render.inlinethought(thought) for thought in thoughts_all()]
        return renderpage.home(thoughts)

class ThoughtServer:
    def GET(self, name):
        thought = thought_get(name)

        if thought is None:
            return web.notfound()

        return renderpage.thought(thought)
		
class TagServer:
	def GET(self, tag):
		thoughts = [render.inlinethought(thought) for thought in thoughts_by_tag(tag)]
		return renderpage.tag(tag, thoughts)
		
if __name__ == "__main__":
    app.run()
