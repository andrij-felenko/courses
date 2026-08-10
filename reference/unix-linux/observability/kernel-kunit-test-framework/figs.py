def render():
    print("Rendering kunit-architecture.svg...")
    with open("kunit-architecture.svg", "w") as f:
        f.write("<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>")
    print("Done")

if __name__ == "__main__":
    render()
