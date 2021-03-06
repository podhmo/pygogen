from egoist.app import create_app, SettingsDict

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = create_app(settings)

# generated by egoist init new-directive --name=foo
app.include("directives.foo:define_foo")


@app.define_foo
def xxx():
    pass


@app.define_foo
def yyy():
    pass


def main():
    print("start main")
    app.commit(dry_run=False)
    print("end main")


if __name__ == "__main__":
    main()
