/hello_salt:
  file.managed:
    - name: /hello_salt
    - contents: "hi"
