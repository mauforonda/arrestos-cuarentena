#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from operator import itemgetter
import re
import csv

def probe():
  url = 'https://www.defensoria.gob.bo/covid-19'
  h = requests.head(url).headers
  return int(re.search('/covid-19/(.*)-dia.html', h['Location']).group(1))

def sofar(output):
  with open(output, 'r') as f:
    reader = csv.reader(f)
    return [row for row in reader]

def get_day(day_number):
  url = 'https://www.defensoria.gob.bo/covid-19/{}-dia.html'
  response = requests.get(url.format(int(day_number)))
  dom = BeautifulSoup(response.text, 'html.parser')
  return dom

def get_date(dom):
  field = dom.select('.col-md-6 .fecha')[0].get_text().strip()
  field_date =  datetime.strptime(field, 'Reporte diario: %d/%m/%Y')
  return datetime.strftime(field_date, '%Y-%m-%d')

def get_reporte(dom):
  data = [get_date(dom)]
  for field in list(dom.select('.covid-19 .row .numero.shadow'))[:-4]:
    data.append(int(field.contents[-1].strip()))
  return data

def save_csv(file_path, reports):
  header = ['arrestos_femenino', 'arrestos_masculino', 'arrestos_no_especifica', 'arrestos_totales', 'liberados_femenino', 'liberados_masculino', 'liberados_no_especifica', 'liberados_totales', 'siguen_detenidos_femenino', 'siguen_detenidos_masculino', 'siguen_detenidos_no_especifica', 'siguen_detenidos_totales']
  with open(file_path, 'w+') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for report in reports:
      writer.writerow(report)

output = 'data.csv'
last_day = probe()
reports = sofar(output)[1:]

if len(reports) != last_day:
  
  for day in range(len(reports) + 1,last_day + 1):
    dom = get_day(day)
    reports.append(get_reporte(dom))
  reports = sorted(reports, key=itemgetter(0))
  save_csv(output, reports)
  print('update')
  
else:

  print('nothing')
