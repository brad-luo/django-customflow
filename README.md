# django-cutomflow

- 该项目是一个高度自定义, 持久化的流程框架.


## Unstallation
First, install the package with pip.  
```bash
pip install django-customflow
```

pip install django-customflow`

Register django_customflow in your list of Django applications:
```python
INSTALLED_APPS = (
    ...,
    'django_customflow',
    ...,
)
```

Then migrate the app to create the database table  
`python manage.py migrate django_customflow`


## Usage
In your models, add the mixin, like:
```python
from django.db import models
from django_customflow.mixins import WorkflowMixin

class TestObj(models.Model, WorkflowMixin):
    ...

```

Then you can use the methods of `WorkflowMixin`. For specific  
usage, please refer to the docs.