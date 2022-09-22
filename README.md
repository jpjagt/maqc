# measuring construction sites

## setup

this contains a list of steps you should take to set up the environment.

### virtualenv

we'll use `virtualenv` to get a separated python environment for our current project.

if you don't have it yet, install it:

```sh
pip install virtualenv
```

then, create a virtualenv for this project, with the name `mcs`:

```sh
virtualenv ~/.virtualenvs/mcs
```

**anytime** you open your terminal, you need first activate this environment with:

```sh
source ~/.virtualenvs/mcs/bin/activate
```

### packages

if you have activated the `mcs` environment, run this to install the required packages:

```sh
pip install -r requirements.txt
```

we will also install our own code as a local package, to circumvent python's
module import hell:

```sh
pip install -e .
```

now, everything in the `mcs` directory will become easy to import: `import mcs.constants`, for instance.

### .env file

last, we need to indicate some values which will be different for everyone,
like the root directory of this project. copy over the example file
`.env.example` to `.env`:

```sh
cp .env.example .env
```

open your `.env` file, and start filling in the values.

any of these values are accessible in python through the `decouple` package:

```python
from decouple import config
value = config("SOME_ENV_VALUE")
```
