package com.sky.service.impl;

import com.sky.constant.StatusConstant;
import com.sky.entity.Orders;
import com.sky.mapper.*;
import com.sky.service.WorkspaceService;
import com.sky.vo.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.*;

@Service
@Slf4j
public class WorkspaceServiceImpl implements WorkspaceService {

    @Autowired private OrderMapper orderMapper;
    @Autowired private UserMapper userMapper;
    @Autowired private DishMapper dishMapper;
    @Autowired private SetmealMapper setmealMapper;

    public BusinessDataVO getBusinessData(LocalDateTime begin, LocalDateTime end) {
        Map<String, Object> map = new HashMap<>();
        map.put("begin", begin);
        map.put("end", end);

        Integer totalOrderCount = orderMapper.countByMap(map);
        map.put("status", Orders.COMPLETED);
        Double turnover = orderMapper.sumByMap(map);
        turnover = turnover == null ? 0.0 : turnover;
        Integer validOrderCount = orderMapper.countByMap(map);

        Map<String, Object> userMap = new HashMap<>();
        userMap.put("end", end);
        userMap.put("begin", begin);
        Integer newUsers = userMapper.countByMap(userMap);

        Double unitPrice = validOrderCount == 0 ? 0.0 : turnover / validOrderCount;
        Double orderCompletionRate = totalOrderCount == 0 ? 0.0 : validOrderCount * 1.0 / totalOrderCount;

        return BusinessDataVO.builder()
                .turnover(turnover)
                .validOrderCount(validOrderCount)
                .orderCompletionRate(orderCompletionRate)
                .unitPrice(unitPrice)
                .newUsers(newUsers)
                .build();
    }

    public OrderOverViewVO getOrderOverView() {
        Map<String, Object> map = new HashMap<>();
        map.put("status", Orders.TO_BE_CONFIRMED);
        Integer waitingOrders = orderMapper.countByMap(map);
        map.put("status", Orders.CONFIRMED);
        Integer confirmedOrders = orderMapper.countByMap(map);
        map.put("status", Orders.DELIVERY_IN_PROGRESS);
        Integer deliveredOrders = orderMapper.countByMap(map);
        Integer allOrders = 0;
        Integer cancelledOrders = 0;
        return OrderOverViewVO.builder()
                .allOrders(allOrders).cancelledOrders(cancelledOrders)
                .waitingOrders(waitingOrders).deliveredOrders(deliveredOrders)
                .completedOrders(0).build();
    }

    public DishOverViewVO getDishOverView() {
        return DishOverViewVO.builder()
                .sold(dishMapper.countByStatus(StatusConstant.ENABLE))
                .discontinued(dishMapper.countByStatus(StatusConstant.DISABLE))
                .build();
    }

    public SetmealOverViewVO getSetmealOverView() {
        return SetmealOverViewVO.builder()
                .sold(setmealMapper.countByStatus(StatusConstant.ENABLE))
                .discontinued(setmealMapper.countByStatus(StatusConstant.DISABLE))
                .build();
    }
}