#!/bin/bash

ifconfig | sed -En 's/inet (192.168.[0-9.]+) netmask.*/\1/p'
