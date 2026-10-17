*** Begin Patch
*** Update File: run_page/utils.py
@@
 def make_activities_file(
     sql_file, data_dir, json_file, file_suffix="gpx", activity_title_dict=None
 ):
-    generator = Generator(sql_file)
-    generator.sync_from_data_dir(
-        data_dir, file_suffix=file_suffix, activity_title_dict=activity_title_dict
-    )
-    activities_list = generator.load()
-    with open(json_file, "w") as f:
-        json.dump(activities_list, f)
+    import os
+    import time
+
+    TRACE = os.getenv("TRACE_GPXSYNC", "0") == "1"
+
+    generator = Generator(sql_file)
+
+    start_all = time.perf_counter()
+    if TRACE:
+        print(f"[GPX-SYNC] start sync_from_data_dir: data_dir={data_dir} file_suffix={file_suffix}")
+    t0 = time.perf_counter()
+    generator.sync_from_data_dir(
+        data_dir, file_suffix=file_suffix, activity_title_dict=activity_title_dict
+    )
+    t1 = time.perf_counter()
+    if TRACE:
+        print(f"[GPX-SYNC] sync_from_data_dir finished: elapsed={t1-t0:.2f}s")
+
+    if TRACE:
+        print(f"[GPX-SYNC] start generator.load()")
+    t0 = time.perf_counter()
+    activities_list = generator.load()
+    t1 = time.perf_counter()
+    if TRACE:
+        print(f"[GPX-SYNC] generator.load() finished: elapsed={t1-t0:.2f}s")
+
+    with open(json_file, "w") as f:
+        json.dump(activities_list, f)
+
+    end_all = time.perf_counter()
+    if TRACE:
+        print(f"[GPX-SYNC] total elapsed={end_all-start_all:.2f}s; wrote {len(activities_list)} activities to {json_file}")
*** End Patch
