
```bash
python ./reading_from_TCP.py --host 127.0.0.1 --output-dir logs/distance --filename 20cm.log
```

```bash
python ./reading_from_TCP.py --host 192.168.137.1 --output-dir logs/distance --filename 20cm.log
```


```bash
python ./plot_single_log.py --epcs E2806995000040154D38514E E2806995000050154D38554E E2806995000050154D384D4E --log-file logs/distance/next_to.log
```

```bash
python ./plot_multiple_logs.py --epcs E2806995000040154D38514E E2806995000050154D38554E E2806995000050154D384D4E --folder ./logs/distance
```

