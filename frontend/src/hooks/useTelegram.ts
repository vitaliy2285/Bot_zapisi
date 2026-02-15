import { useEffect } from 'react';

type TelegramWebApp = {
  ready: () => void;
  expand: () => void;
  initData: string;
  MainButton: {
    setText: (text: string) => void;
    show: () => void;
    hide: () => void;
    onClick: (fn: () => void) => void;
    offClick: (fn: () => void) => void;
  };
  BackButton: {
    show: () => void;
    hide: () => void;
    onClick: (fn: () => void) => void;
    offClick: (fn: () => void) => void;
  };
  HapticFeedback: {
    notificationOccurred: (type: 'success' | 'warning' | 'error') => void;
    impactOccurred: (style: 'light' | 'medium' | 'heavy') => void;
  };
};

export function useTelegram() {
  const tg = (window as Window & { Telegram?: { WebApp?: TelegramWebApp } }).Telegram?.WebApp;

  useEffect(() => {
    if (!tg) {
      return;
    }
    tg.ready();
    tg.expand();
  }, [tg]);

  return {
    tg,
    initData: tg?.initData ?? '',
    setMainButton(text: string, onClick: () => void) {
      if (!tg) {
        return () => undefined;
      }
      tg.MainButton.setText(text);
      tg.MainButton.show();
      tg.MainButton.onClick(onClick);
      return () => {
        tg.MainButton.offClick(onClick);
        tg.MainButton.hide();
      };
    },
    setBackButton(onClick: () => void) {
      if (!tg) {
        return () => undefined;
      }
      tg.BackButton.show();
      tg.BackButton.onClick(onClick);
      return () => {
        tg.BackButton.offClick(onClick);
        tg.BackButton.hide();
      };
    },
    hapticSuccess() {
      tg?.HapticFeedback.notificationOccurred('success');
    },
    hapticError() {
      tg?.HapticFeedback.notificationOccurred('error');
    },
  };
}
