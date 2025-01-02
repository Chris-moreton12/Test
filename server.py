from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import os

# A simple in-memory store for users
users = {}

# Recipes dictionary
recipes = {
    "sponge cake": {"eggs", "flour", "butter", "sugar"},
    "pancakes": {"eggs", "flour", "milk", "sugar"},
    "cookies": {"flour", "butter", "sugar", "chocolate chips"},
}


class BakingHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        parsed_data = urlparse.parse_qs(post_data)

        if self.path == "/signup":
            username = parsed_data["username"][0]
            password = parsed_data["password"][0]
            if username in users:
                self.respond_with_message("User already exists!")
            else:
                users[username] = password
                self.respond_with_message("Signup successful! Go to login page.")
        elif self.path == "/login":
            username = parsed_data["username"][0]
            password = parsed_data["password"][0]
            if users.get(username) == password:
                self.respond_with_file("dashboard.html")
            else:
                self.respond_with_message("Invalid credentials!")
        elif self.path == "/recipes":
            ingredients = set(parsed_data["ingredients"][0].split(","))
            available_recipes = [
                recipe for recipe, req_ingredients in recipes.items() if req_ingredients.issubset(ingredients)
            ]
            self.respond_with_message(f"Recipes you can make: {', '.join(available_recipes)}")

    def respond_with_file(self, filename):
        if os.path.exists(filename):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open(filename, "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found!")

    def respond_with_message(self, message):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(f"<html><body><h1>{message}</h1></body></html>".encode("utf-8"))


def run(server_class=HTTPServer, handler_class=BakingHTTPRequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
