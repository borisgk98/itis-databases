# itis-databases
Домашние задания по курсу "Системы управления хранилищами данных", ИТИС, 4 курс

## Задание 2
Пункты 1-3 я выполнял на aws, для остальных заданий я разворачивал собственную инфраструктуру.
#### 1.
Настройка aws
```
aws configure
```
Получение доступных узлов
```
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[*].{Instance:InstanceId,Subnet:SubnetId,State:State.Name}' \
    --output json
```
#### 2.
Создание инстанса
```
aws opsworks --region us-east-1 create-instance --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --layer-ids 5c8c272a-f2d5-42e3-8245-5bf3927cb65b --hostname myinstance1 --instance-type m1.large --os "Amazon Linux"
```
#### 3.
Проверка связи с помощью команды `ping`

#### 4-5.
Далее для разворачивания cassandra и системы мониторинга я использовал кластер на основе [microk8s](https://microk8s.io/) на базе Ubuntu.
Установка
```
sudo snap install microk8s --classic
```
Включение службы dns, службы [мониторинга prometheus](https://github.com/prometheus-operator/prometheus-operator), [службы для создания балансировщиков нагрузки](https://metallb.universe.tf/usage/), пакетный менаджер helm, дополненние storage (позволяет использовать и создавать ресурсы для хранилища)
```
microk8s enable dns prometheus metallb helm3 storage
```
Для установки cassandra в кластер будем использовать helm и подготовленный helm-chart https://github.com/bitnami/charts/tree/master/bitnami/cassandra
Параметры, которые нам надо поменять для установки:
- dbUser.user = admin (пользователь касандры)
- dbUser.password = cassPass1234 (пароль касандры)
- replicaCount = 3 (количество узлов касандры)
- metrics.enabled = true (включаем метрики)
- metrics.serviceMonitor.namespace = monitoring (пространство имен для системы мониторинга)
- metrics.serviceMonitor.enabled = true (включаем ServiceMonitoring для сервисов касандры)
- service.type = LoadBalancer (тип сервиса - балансировщик награзки)

Устанавливаем cassandra:
```
helm install cassandra --namespace=default --values=hw2/cassandra-helm-values.yaml bitnami/cassandra
```
#### 6.
В качестве сервера для тестирования я буду использовать свой ноутбук (заместо четвертого узла ec2).
#### 7.
Создание таблицы
```
CREATE KEYSPACE test WITH REPLICATION = {
   'class' : 'SimpleStrategy',
   'replication_factor' : 1
  };

CREATE TABLE test.TEST (
    id int primary key,
    name text
);
```
Программа для заполненния: [hw2/generator.py](https://github.com/borisgk98/itis-databases/blob/main/hw2/generator.py)
#### 8.
Для определения количества записей на каждом узле используем nodetool
```
kubectl exec -it cassandra-2 -- nodetool cfstats test.test | grep "Write Count"
```
Для создания графика я использовал matplotlib. [Исходный код](https://github.com/borisgk98/itis-databases/blob/main/hw2/histogram.py)
![Разпределение данных по узлам](https://github.com/borisgk98/itis-databases/blob/main/hw2/histogram.png)

## Задание 3
#### 1-2.
В задание 2 уже настроен prometheus operator для сбора метрик
#### 3.
Тут нужно настроить графики в графане.
Для соединения с графаной используем следующую команду:
```
kubectl -n monitoring port-forward grafana-7c9bc466d8-lbgr9 3000:3000
```
После настройки графиков ([сам дашборд для кассандры](https://github.com/borisgk98/itis-databases/blob/main/hw3/cassandra-dashboard.json))) получаем следующую картину:
![График](https://github.com/borisgk98/itis-databases/blob/main/hw3/grafana.png)

## Задание 5
#### 1.
Используем генератор из первого задания
#### 2.
#### 3. 
Тут сложнее так как в качетсве среды мы используем kubernetes. При запуске инстанса касандры создается один особый процесс с PID=1, SIGKILL данного процесса приводит к заверешение работы узла ПОЛНОСТЬЮ и перезапуску его контроллером репликации. Поэтому для симуляции завершения работы узла я использовал следующий код:
```
while true; do kubectl delete pod cassandra-0; sleep 1; done
```

Для доступа к конкретному узлу касандры используется следующая команда:
```
kubectl exec -it cassandra-1 -- /bin/bash
```

#### 4.

Проверяем статус касандры до отключения:
```
@cassandra-1:/$ nodetool status
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address       Load       Tokens       Owns (effective)  Host ID                               Rack
UN  10.1.220.201  4.45 MiB   256          32.9%             af740fc7-eb2b-4499-8c2d-d3d6f15ad367  rack1
UN  10.1.220.203  4.62 MiB   256          33.4%             233c5e9b-46ff-4a2d-a49d-df20201b089b  rack1
UN  10.1.220.205  5.39 MiB   256          33.7%             ab44539b-cf42-4886-9572-fa2bb65363e1  rack1
```

Проверяем статус касандры после отключения:
```
@cassandra-2:/$ nodetool status
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address       Load       Tokens       Owns (effective)  Host ID                               Rack
DN  10.1.220.209  6.81 MiB   256          33.4%             233c5e9b-46ff-4a2d-a49d-df20201b089b  rack1
UN  10.1.220.212  6.63 MiB   256          32.9%             af740fc7-eb2b-4499-8c2d-d3d6f15ad367  rack1
UN  10.1.220.216  6.8 MiB    256          33.7%             ab44539b-cf42-4886-9572-fa2bb65363e1  rack1
```

![График после отключения узла](https://github.com/borisgk98/itis-databases/blob/main/hw5/cassandra-dashboard-node-off.png)

Проверяем статус касандры после включения:
```
@cassandra-2:/$ nodetool status
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address       Load       Tokens       Owns (effective)  Host ID                               Rack
UN  10.1.220.225  7.62 MiB   256          33.4%             233c5e9b-46ff-4a2d-a49d-df20201b089b  rack1
UN  10.1.220.212  6.62 MiB   256          32.9%             af740fc7-eb2b-4499-8c2d-d3d6f15ad367  rack1
UN  10.1.220.216  6.8 MiB    256          33.7%             ab44539b-cf42-4886-9572-fa2bb65363e1  rack1
```

![График после включения узла](https://github.com/borisgk98/itis-databases/blob/main/hw5/cassandra-dashboard-node-on.png)

## Задание 6
В качестве LoadBalancer в моем решении используется [MetalLB](https://github.com/metallb/metallb). Настройка данного решения происходила во втором задании.
[Файл конфигурации](https://github.com/borisgk98/itis-databases/blob/main/hw2/config.yaml)

На графике ниже видно распределение входящего трафика на узлы касандры.

![График трафика](https://github.com/borisgk98/itis-databases/blob/main/hw6/lb.png)
