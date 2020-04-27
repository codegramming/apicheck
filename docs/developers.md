---
layout: doc
title: Building new tools
permalink: /docs/building-new-tools
---

<a id="why-create-new-a-tool"></a>
# Why create a new tool

APICheck is comprised by a set of tools that combined together can provide a lot
of different functionality. APICheck can not only integrate self-developed tools,
but also can leverage on existing tools in order to take advantage of them to
provide new functionality.

Either you wish to develop a new cool tool or integrate an already existing tool
you need to follow som steps in order to make it available in APICheck. At this
point this is the document you need to read.


<a id="tools-philosophy"></a>
# Tools philosophy

## Packaging

Each tool in APICheck is a Docker image. This means that tools are a *black box*
that could receive some information into its standard input and write results
in the standard output and or error. Aditionally the return code can be used to
stop the current chain.

Inside the Docker image developers are free to install any tool they think it's
necessary.

## Meta information

Every tool needs to provide some information in order to be properly managed by
the *Package Manager* and to give information that helps users to know what the
tools does. Among this information are items such as:

- Tool nane
- version
- Description
- ...

## Automating the integration of new tools

APICheck leverages on build automation to mantatain al publish the set of tools
currently available. Each time a developer adds or modifies a tool (via a pull
request), the build process will be launch to generate a new release for the
tool.


<a id="apicheck-and-pipelines"></a>
# APICheck and pipelines

APICheck was made as a small set of tools but they can be interact, borrowing the UNIX pipelines:

![APICheck UNIX Pipeline](/apicheck/assets/images/apicheck_unix_pipeline.png)

<a id="apicheck-data-format"></a>
# APICheck data format

As we said APICheck was made with *pipeline* concept in mind. So, to communicate tools between them they must share a common format. This is that we call *APICheck data Format*.

The format is very easy: A JSON with these keys:

- request
- response
- _meta

The complete JSON format example, as pretty display:

```json
{
  "_meta": {
    "host": "nvd.nist.gov",
    "schema": "https",
    "tool1": {
        "custom_results": "custom results that output from tool 1"
    }
  },
  "request": {
    "path": "/",
    "method": "get",
    "headers": {
      "User-Agent": "curl/7.54.0",
      "Accept": "*/*"
    },
    "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"
  },
  "response": {
    "status": 200,
    "reason": "Ok",
    "headers": {},
    "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"
  }
}
```
&#9888; This is NOT a valid JSON file for APICheck. Check [One line format section](#one-line-format)

## Important notes about data format

### Progressing data through pipeline

This file must progress through tools pipeline. The idea is that not only the first tool in the pipe receive the information, also the ending tools must receive it.

### Body encoding

The body key is encoded as base64. The reason is to allow to put inside any kind of data, no only text: images, random binary files, JSON...

This mind that *tools that receives the JSON must decode this field*.  

### The '_meta'

So this file must progress between each pipeline step. Each tool can add their results or something else at *_meta* key. This key is a free field that tools can fill.

<a id="one-line-format"></a>
### One JSON line format

The above example is not really valid for data for APICheck data format.

To be APICheck compliant the JSON must be represented as: *One JSON per line*. The above example should be represented as:

```json
{"_meta": null, "request": {"url": "https://nvd.nist.gov/", "method": "get", "headers": {"User-Agent": "curl/7.54.0", "Accept": "*/*"}, "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"}, "response": {"status": 200, "reason": "Ok", "headers": {}, "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"}}
```

The reason to do that is to allow data streaming. JSON is not a format that was designed for streaming. To overcome this limitation and allow to send more than 1 data in a pipeline, and having in count that tools will read from stdin, they will read line by line the standard system input. So, each time they read a line they will be reading a complete data from previous step.

Example of 3 input data:

```console
$ cat 3_apicheck_data.json
{"_meta": null, "request": {"url": "https://google.com/", "method": "post", "headers": {"User-Agent": "curl/7.54.0", "Accept": "*/*"}, "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"}, "response": {"status": 200, "reason": "Ok", "headers": {}, "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"}}
{"_meta": null, "request": {"url": "https://www.skype.com/", "method": "head", "headers": {"User-Agent": "curl/7.54.0", "Accept": "*/*"}, "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"}, "response": {"status": 200, "reason": "Ok", "headers": {}, "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"}}
{"_meta": null, "request": {"url": "https://nvd.nist.gov/", "method": "get", "headers": {"User-Agent": "curl/7.54.0", "Accept": "*/*"}, "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"}, "response": {"status": 200, "reason": "Ok", "headers": {}, "body": "ewogICAgInVzZXJuYW1lIjogIm1lQG1lLmNvbSIsCiAgICAicGFzc3dvcmQiOiAia3NrbGFzZGYiCn0K"}}
$ cat 3_apicheck_data.json | sensitive-json | pretty-display
```  

<a id="steps-for-creating-a-new-tool"></a>
# Steps for creating a new tool

Well, if you're here this mind that you're interested in how to create a new tool. You must follow these steps:

## Steps summary:

In summary we'll need to do these things:

1. Fork APICheck repo
2. Clone forked repo
3. Creates a new folder in */tools* directory.
4. Add files: META, README.md and Dockerfile
5. Push the repo to our account in Github
6. Send us a Pull Request

## Step 1 - fork Github repo

This step don't need more explanation :)

## Step 2 - clone your forked repo

```console
$ git clone https://github.com/[YOUR-GITHUB-USER]/apicheck
```

It was the easy part :)

## Step 3 - create a the tool folder

APICheck tools are inside */tools* folder. Each tool has their own folder.

Folders names can contain: numbers, letters and "_" or "-".

Then, we create a new folder for your tool:

```console
$ cd tools/
$ mkdir hello-world-tool
```

## Step 4 - Include Meta information

Meta information is contained in a file called *META*. Format of this file is a key, value with a "=" symbol.

You must include **all** of these fields for a valid META file:

- *name*: tools name. This name will be used for catalog, Docker image and for installing the tool. **Must be unique**. *This field only can contains: Letters, numbers and "-" / "_" symbols*.
- *short-command* (optional): some times tool name is too long. short command is easy to typing alias. when you'r tool was intalled by the package-manage, it will creates 2 commands name. One of them will be the name of the tool and the other command will be a short command for the tool. **Must be unique**.
- *display-name*: text that you want to be displayed in the catalog.
- *version*: version of the tool. It's recommendable to follow semantic format, but you're free to put use you're version format
- *description*: a description of your tool. Try to be descriptive. There's not limit for description long, but we recommend not more than 150 characters.
- *home*: author can include a link of the tool home, their profile os something else. This field is open.
- *author*: author name or team

You must put the *META* file in the root of the folder we just created for our tool:

```console
$ cd tools/
$ cd hello-world-tool/
$ cat META
name = hello-world-tool
short-command = ac-hwt
version = 1.0.0
description = All good tutorials must include a Hello World example! :)
home = https://github.com/BBVA/apicheck
author = BBVA Labs Security
```

## Step 5 - Include tool documentation

Each tool must include their own documentation file. This is very important part of your tool.

Documentation must be write in Markdown format. It must be included in the root of your folder tool and must be called **README.md**:

```console
$ cd tools/
$ cd hello-world-tool/
$ cat README.md
# Hello Word Tool Documentation

Wellcome to the demo tool of APICheck tutorial

## How to install
....
```

&#9888; Be careful with the name of file, the name must be in upper case and the extension in lower case.

## Step 6 - Include the Dockefile

As we said a tool will be packed as a Docker Image, so we need a Dockerfile.

You can write the Dockerfile you need to package your tool but if you minimize the resulting Docker Image will be useful for users.

```console
$ cd tools/
$ cd hello-world-tool/
$ cat Dockerfile
FROM python:3.8-alpine

RUN apk update \
    && apk add --no-cache build-base
...
```

## Step 7 - Push your new plugin to Github

At this point we only need to commit and push the new plugin to Github:

```console
$ git add tools/hello-world-tool/
$ git commit -am "my first APICheck tool!"
$ git push
```

### Step 8 - Send us a Pull Request

Only "click" in the "New pull request" button at Github:

![Send us a Pull Request](/apicheck/assets/images/doc_develop_pull_request.png)


<a id="faq"></a>
# F.A.Q.

## I need to develop in a specific language?

Absolutely no! You can develop in your favorite code language. Some member os the APICheck team loves Bash and some tools was integrade without codding any line.

Have in mind that each tool are packaged in a Docker Image. Inside this Docker Image you're the king/Queen. You can install all you need to build your tools.

## Is there any good practice for building tools?

- Build small docker images as you can
- Don't use tool name that already exits as part of APICheck ecosystem

## I updated my tool, but no new release was published

As the building process is automated it only raises if you modify something at the *META* file.

If you're releasing a new tool version, be sure you update the version number in *META* file.