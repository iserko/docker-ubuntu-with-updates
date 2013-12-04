# docker-ubuntu-with-updates

`Dockerfile` for producing Ubuntu images with all updates and security patches applied.

## Getting started

Dependencies:

* [Docker](http://docker.io)
* [Shipper](https://github.com/mailgun/shipper)

Running it:

    make env
    source .ve/bin/activate

    # just build a precise image in your local machine
    make precise

    # build a precise image for today and push to docker registry.
    make precise-upload
