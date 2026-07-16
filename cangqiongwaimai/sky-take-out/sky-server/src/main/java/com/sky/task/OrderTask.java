package com.sky.task;

import com.alibaba.fastjson.JSON;
import com.sky.entity.Orders;
import com.sky.mapper.OrderMapper;
import com.sky.websocket.WebSocketServer;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.*;

@Component
@Slf4j
public class OrderTask {
    @Autowired
    private OrderMapper orderMapper;
    @Autowired
    private WebSocketServer webSocketServer;

    @Scheduled(cron = "0 * * * * ?")
    public void processTimeoutOrder(){
        log.info("处理支付超时订单：{}", new Date());
        LocalDateTime time = LocalDateTime.now().plusMinutes(-15);
        List<Orders> ordersList = orderMapper.getByStatusAndOrdertimeLT(Orders.PENDING_PAYMENT, time);
        if(ordersList != null && !ordersList.isEmpty()){
            ordersList.forEach(order -> {
                order.setStatus(Orders.CANCELLED);
                order.setCancelReason("支付超时，自动取消");
                order.setCancelTime(LocalDateTime.now());
                orderMapper.update(order);
            });
            pushOrderNotification("处理超时订单", ordersList.size() + " 笔订单已自动取消");
        }
    }

    @Scheduled(cron = "0 0 1 * * ?")
    public void processDeliveryOrder(){
        log.info("处理派送中订单：{}", new Date());
        LocalDateTime time = LocalDateTime.now().plusMinutes(-60);
        List<Orders> ordersList = orderMapper.getByStatusAndOrdertimeLT(Orders.DELIVERY_IN_PROGRESS, time);
        if(ordersList != null && !ordersList.isEmpty()){
            ordersList.forEach(order -> {
                order.setStatus(Orders.COMPLETED);
                orderMapper.update(order);
            });
            pushOrderNotification("处理已派送订单", ordersList.size() + " 笔订单已自动完成");
        }
    }

    private void pushOrderNotification(String title, String detail) {
        Map<String, Object> map = new HashMap<>();
        map.put("type", 1);
        map.put("title", title);
        map.put("content", detail);

        // 统计当前各状态订单数
        map.put("pendingPayment", countByStatus(Orders.PENDING_PAYMENT));
        map.put("toBeConfirmed", countByStatus(Orders.TO_BE_CONFIRMED));
        map.put("confirmed", countByStatus(Orders.CONFIRMED));
        map.put("deliveryInProgress", countByStatus(Orders.DELIVERY_IN_PROGRESS));

        webSocketServer.sendToAllClient(JSON.toJSONString(map));
    }

    private Integer countByStatus(Integer status) {
        Map<String, Object> m = new HashMap<>();
        m.put("status", status);
        Integer count = orderMapper.countByMap(m);
        return count == null ? 0 : count;
    }
}
