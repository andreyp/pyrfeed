#!/usr/bin/env python
# -*- coding : iso-8859-1 -*-

from SmartQuery.Handler import QueryHandler

import reader_query as reader_query
q = QueryHandler( queries=reader_query.queries )
q.writeo( 'reader_query' )
