################################################################################
# Makefile for xsconsole
# Copyright (c) Citrix Systems 2007

PREFIX=$(DESTDIR)/usr
LIBDIR=$(DESTDIR)/usr/lib64/

INSTALL=/usr/bin/install

BIN_MODE := 755
LIB_MODE := 644
DOC_MODE := 644


################################################################################
# List of python scripts:
SCRIPTS :=
SCRIPTS += XSConsole.py
SCRIPTS += XSConsoleAuth.py
SCRIPTS += XSConsoleBases.py
SCRIPTS += XSConsoleConfig.py
SCRIPTS += XSConsoleCurses.py
SCRIPTS += XSConsoleData.py
SCRIPTS += XSConsoleDataUtils.py
SCRIPTS += XSConsoleDialogueBases.py
SCRIPTS += XSConsoleDialoguePane.py
SCRIPTS += XSConsoleFields.py
SCRIPTS += XSConsoleHotData.py
SCRIPTS += XSConsoleImporter.py
SCRIPTS += XSConsoleKeymaps.py
SCRIPTS += XSConsoleLang.py
SCRIPTS += XSConsoleLangErrors.py
SCRIPTS += XSConsoleLangFriendlyNames.py
SCRIPTS += XSConsoleLog.py
SCRIPTS += XSConsoleLayout.py
SCRIPTS += XSConsoleMenus.py
SCRIPTS += XSConsoleMetrics.py
SCRIPTS += XSConsoleRemoteTest.py
SCRIPTS += XSConsoleRootDialogue.py
SCRIPTS += XSConsoleStandard.py
SCRIPTS += XSConsoleState.py
SCRIPTS += XSConsoleTask.py
SCRIPTS += XSConsoleTerm.py
SCRIPTS += XSConsoleUtils.py
SCRIPTS += simpleconfig.py

PLUGINS_BASE :=
PLUGINS_BASE += XSFeatureChangePassword.py
PLUGINS_BASE += XSFeatureChangeTimeout.py
PLUGINS_BASE += XSFeatureCrashDumpSR.py
PLUGINS_BASE += XSFeatureDRBackup.py
PLUGINS_BASE += XSFeatureDRRestore.py
PLUGINS_BASE += XSFeatureDRSchedule.py
PLUGINS_BASE += XSFeatureDNS.py
PLUGINS_BASE += XSFeatureDisplayNICs.py
PLUGINS_BASE += XSFeatureEULA.py
PLUGINS_BASE += XSFeatureHostCommon.py
PLUGINS_BASE += XSFeatureHostEvacuate.py
PLUGINS_BASE += XSFeatureHostInfo.py
PLUGINS_BASE += XSFeatureInterface.py
PLUGINS_BASE += XSFeatureKeyboard.py
PLUGINS_BASE += XSFeatureLocalShell.py
PLUGINS_BASE += XSFeatureLogInOut.py
PLUGINS_BASE += XSFeatureNetworkReset.py
PLUGINS_BASE += XSFeatureNTP.py
PLUGINS_BASE += XSFeatureQuit.py
PLUGINS_BASE += XSFeaturePoolEject.py
PLUGINS_BASE += XSFeaturePoolJoin.py
PLUGINS_BASE += XSFeaturePoolNewMaster.py
PLUGINS_BASE += XSFeatureReboot.py
PLUGINS_BASE += XSFeatureRemoteShell.py
PLUGINS_BASE += XSFeatureSRCommon.py
PLUGINS_BASE += XSFeatureSRCreate.py
PLUGINS_BASE += XSFeatureSRInfo.py
PLUGINS_BASE += XSFeatureSaveBugReport.py
PLUGINS_BASE += XSFeatureFullVersion.py
PLUGINS_BASE += XSFeatureShutdown.py
PLUGINS_BASE += XSFeatureStatus.py
PLUGINS_BASE += XSFeatureSuspendSR.py
PLUGINS_BASE += XSFeatureSyslog.py
PLUGINS_BASE += XSFeatureSystem.py
PLUGINS_BASE += XSFeatureTestNetwork.py
PLUGINS_BASE += XSFeatureTimezone.py
PLUGINS_BASE += XSFeatureUploadBugReport.py
PLUGINS_BASE += XSFeatureValidate.py
PLUGINS_BASE += XSFeatureVMCommon.py
PLUGINS_BASE += XSFeatureVMInfo.py
PLUGINS_BASE += XSMenuLayout.py

PLUGINS_OEM :=
PLUGINS_OEM += XSFeatureClaimSR.py
PLUGINS_OEM += XSFeatureLicenseNag.py
PLUGINS_OEM += XSFeatureManagementHelp.py
PLUGINS_OEM += XSFeatureOEMBackup.py
PLUGINS_OEM += XSFeatureOEMRestore.py
PLUGINS_OEM += XSFeatureReset.py
PLUGINS_OEM += XSFeatureUpdate.py
PLUGINS_OEM += XSFeatureVerboseBoot.py
PLUGINS_OEM += XSMenuOEMLayout.py

PLUGINS_EXTRAS :=

ALL_SCRIPTS := $(SCRIPTS)
ALL_SCRIPTS += $(addprefix plugins-base/, $(PLUGINS_BASE))
ALL_SCRIPTS += $(addprefix plugins-oem/, $(PLUGINS_OEM))
ALL_SCRIPTS += $(addprefix plugins-extras/, $(PLUGINS_EXTRAS))

################################################################################
# Executable:
COMMAND := xsconsole

################################################################################

DEFAULT: minimaltest

################################################################################
install-base:
	mkdir -p $(LIBDIR)/xsconsole/
	mkdir -p $(LIBDIR)/xsconsole/plugins-base
	mkdir -p $(LIBDIR)/xsconsole/plugins-extras

	$(foreach script,$(SCRIPTS),\
          $(INSTALL) -m $(LIB_MODE) $(script) $(LIBDIR)/xsconsole;)

	$(foreach script,$(PLUGINS_BASE),\
          $(INSTALL) -m $(LIB_MODE) plugins-base/$(script) $(LIBDIR)/xsconsole/plugins-base;)

	$(foreach script,$(PLUGINS_EXTRAS),\
          $(INSTALL) -m $(LIB_MODE) plugins-extras/$(script) $(LIBDIR)/xsconsole/plugins-extras;)

	$(INSTALL) -m $(BIN_MODE) $(COMMAND) $(PREFIX)/bin

#	$(foreach docfile,$(DOCUMENTS),\
#          $(INSTALL) -m $(DOC_MODE) $(docfile) $(DOCDIR);)

	mkdir -p $(PREFIX)/lib/systemd/system
	$(INSTALL) -m $(LIB_MODE) xsconsole.service $(PREFIX)/lib/systemd/system

install-oem:
	mkdir -p $(LIBDIR)/xsconsole/plugins-oem

	$(foreach script,$(PLUGINS_OEM),\
          $(INSTALL) -m $(LIB_MODE) plugins-oem/$(script) $(LIBDIR)/xsconsole/plugins-oem;)

.PHONY: clean
clean:
	rm -f *.pyc
	rm -f */*.pyc
	rm -rf __pycache__ */__pycache__
	rm -rf .mypy_cache .pytest_cache
	rm -rf .git/pre-commit.env .git/pre-commit-pylint.log

depend:

.PHONY: test
test:
	python -m unittest discover

all:

# Convenience targets for pylint output
pylint.txt: .pylintrc $(ALL_SCRIPTS)
	if [ -f $@ ]; then mv $@ $@.tmp; fi
	pylint -j2 --output-format text $(ALL_SCRIPTS) > $@
	# Show new/different warnings in stdout
	if [ -f $@.tmp ]; then diff $@.tmp $@ | grep -E '^[<>]\s*[CRWE]' | cat ; fi
	rm -f $@.tmp

.git/pre-commit.env/bin/pip:
	python3 -m virtualenv .git/pre-commit.env

.git/pre-commit.env/bin/pre-commit: .git/pre-commit.env/bin/pip Makefile
	.git/pre-commit.env/bin/pip install --quiet --upgrade pre-commit

minimaltest: .git/pre-commit.env/bin/pre-commit
	@.git/pre-commit.env/bin/pre-commit run ||                                                        \
	{                                                                                                 \
	 EXIT_CODE=$$?;                                                                                   \
	 echo "----------------------------------------------------------------------------------------"; \
	 echo "If you see the output of 'git diff' above, it shows the changes which pre-commit made.";   \
	 echo "Run 'git add -p' to add those changes to the index and then call make minimaltest again."; \
	 echo "----------------------------------------------------------------------------------------"; \
	 exit $$EXIT_CODE;                                                                                \
	}
	@[ -e .git/hooks/pre-commit ] || \
	 echo "Please run make minimaltest-install"

minimaltest-install: minimaltest
	.git/pre-commit.env/bin/pre-commit install

minimaltest-uninstall: .git/pre-commit.env/bin/pre-commit
	.git/pre-commit.env/bin/pre-commit uninstall
