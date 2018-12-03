from django.urls import path, re_path, include
from . import views
from . import api

# Django doesn't allow url that doesn't include trailing slash...
# https://stackoverflow.com/questions/42212122/why-django-urls-end-with-a-slash
urlpatterns = [
    # GET /keyValue-store/<key> -d “payload=<payload>”
    # PUT /keyValue-store/<key> -d “val=<value>&&payload=<payload>”
    # DELETE  /keyValue-store/<key> -d “payload=<payload>”
    path('keyValue-store/<key>', api.keyValue_store, name='keyValue_store_gpd'),
    path('keyValue-store/', api.empty_put, name='keyValue_store_gpd'),

    # SEARCH /keyValue-store/search/<key> -d “payload=<payload>”
    path('keyValue-store/search/<key>', api.keyValue_store,
         name='keyValue_store_get_search'),
    path('node-info', api.node_info, name="node_info"),
    path('update-node', api.update_node, name="update_node"),
    path('add-view', api.add_view, name="update_node"),
    # GET /view
    # PUT  /view    -d “ip_port=<NewIPPort>”
    # DELETE /view  -d “ip_port=<RemovedIPPort>”
    path('view', api.view, name="view_get"),

    re_path(r'^shard/(?P<route>.*)$', api.shards_api, name='sharding')
]
