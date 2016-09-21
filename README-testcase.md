Dependencies
=================

This test case depends on the following things being installed:

* Python 2.7
  * `subprocess32` package. Install via `sudo pip install subprocess32`
  * (If you're missing pip, `sudo easy_install pip`)
* Git
* Java JDK 1.8
* Ant
* Maven
* Gradle

Running
=========

`python fetch.py` will download the corpus and all internal dependencies (randoop, daikon, junit, do-like-javac, etc.).

`python run.py` will attempt to run Randoop on each project in the corpus. Randoop currently appears to have errors with boofcv, box2d, and dyn4j.

`python run.py --with-daikon` will additionally attempt to run Daikon on the Randoop-generated test cases. Some of these (particularly imgscalr, but possibly others) will run forever if not forcibly killed.

Using Different Versions of Randoop/Daikon
============================================================

To use a different version of Randoop/Daikon, after you run `python fetch.py`, simply replace `randoop.jar` or `daikon.jar` in the `libs` folder created by `python fetch.py` with the version you want to test with.
