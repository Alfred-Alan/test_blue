# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

# from django.test import TestCase

# Create your tests here.
for i in range(1,10):
    for j in range(1,i+1):
        print("{} * {} = {}\t".format(j,i,i*j),end='')
    print('\n')


for i in range(9,0,-1):
    for j in range(i,0,-1):
        print("{} * {} = {}\t".format(j, i, i * j), end='')
    print('\n')